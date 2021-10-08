# knowledgeBase_dataProcess
read data, then do some cleaning and human check, finally setup a KG database( jsondl ).At the same time, Analyze the distribution of entities and relationships, count the number of entities, relationships, and triples, and count the coverage of FVQA, OKVQA, and VQA2.0 in the currently built knowledge base

## 简单写一点程序的说明，方便之后的回顾和代码的整合
```deal_data.py```主要实现的功能就是读入一个fvqa的类似知识库的数据，然后对他里面的内容进行一个筛选，选取自己要的如head，tail，relation之类的内容，然后进行数据清洗，即answer filter，此时可以看到关系和实体的分布情况，并且显示统计结果，以及当前构建的知识库在三个数据集fvqa，okvqa，vqa2.0下的覆盖率，最后是将知识库存储为jsondl格式。<br>
## 接下来从三个子模块进行简单的分析，并介绍github中每个文件名的意义
1. ```get_new_all_json()```函数 <br>
2. ```human_check()```函数 <br>
3. ```convertjson2jsondl()```函数 <br>

