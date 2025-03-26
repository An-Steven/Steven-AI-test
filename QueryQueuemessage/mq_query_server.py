from flask import Flask, request, jsonify
import pymqi
import logging

app = Flask(__name__)

class MQConnectionManager:
    def __init__(self, mq_server):
        try:
            parts = mq_server.split(':')
            self.channel = parts[2] if len(parts) > 2 else 'SYSTEM.DEF.SVRCONN'
            self.host = parts[0]
            self.port = parts[1] if len(parts) > 1 else '1414'
            self.conn_info = f'{self.host}({self.port})'
            self.queue_manager = 'QM1'
            
            self.conn = pymqi.connect(self.queue_manager,
                                    pymqi.CD(Channel=self.channel, ConnectionName=self.conn_info),
                                    pymqi.CMQC.MQCNO_RECONNECT)
        except Exception as e:
            logging.error(f'Connection failed: {str(e)}')
            raise

    def get_connection(self):
        return self.conn

@app.route('/query', methods=['POST'])
def query_messages():
    try:
        data = request.json
        mq_server = data['mq_server']
        queue_name = data['queue_name']
        search_text = data['search_text']

        conn_mgr = MQConnectionManager(mq_server)
        qmgr = conn_mgr.get_connection()
        
        queue = pymqi.Queue(qmgr, queue_name)
        messages = []
        
        while True:
            try:
                message = queue.get(None, pymqi.CMQC.MQGMO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING)
                if search_text.lower() in message.decode().lower():
                    messages.append(message.decode())
            except pymqi.MQMIError as e:
                if e.comp == pymqi.CMQC.MQCC_FAILED and e.reason == pymqi.CMQC.MQRC_NO_MSG_AVAILABLE:
                    break
                else:
                    raise
        
        queue.close()
        qmgr.disconnect()
        
        return jsonify({
            'status': 'success',
            'match_count': len(messages),
            'messages': messages
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)