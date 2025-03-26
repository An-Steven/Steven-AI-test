import argparse
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
import numpy as np

# 初始化模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 配置命令行参数
parser = argparse.ArgumentParser(description='分析Excel文件中描述的相似度')
parser.add_argument('--file', required=True, help='Excel文件路径')
parser.add_argument('--sheet', required=True, help='要处理的Sheet名称')
parser.add_argument('--output', default='result.csv', help='输出文件路径')
parser.add_argument('--eps', type=float, default=0.5, help='DBSCAN聚类半径参数')


def main():
    args = parser.parse_args()

    # 读取Excel数据
    try:
        df = pd.read_excel(args.file, sheet_name=args.sheet)
    except Exception as e:
        print(f"读取文件失败: {e}")
        return

    # 提取描述文本
    descriptions = df['description'].astype(str).tolist()

    # 生成文本嵌入
    embeddings = model.encode(descriptions)

    # 使用DBSCAN聚类
    clustering = DBSCAN(eps=args.eps, min_samples=2).fit(embeddings)
    labels = clustering.labels_

    # 统计聚类结果
    df['cluster'] = labels
    result = df.groupby('cluster')['description']\
        .agg(['count', lambda x: x.mode()[0]])
    result.columns = ['出现次数', '典型描述']

    # 保存结果
    result.to_csv(args.output)
    print(f"分析完成，结果已保存至 {args.output}")


if __name__ == '__main__':
    main()