# knowledgeBase_dataProcess
read data, then do some cleaning and human check, finally setup a KG database( jsondl ).At the same time, Analyze the distribution of entities and relationships, count the number of entities, relationships, and triples, and count the coverage of FVQA, OKVQA, and VQA2.0 in the currently built knowledge base

## 简单写一点程序的说明，方便之后的回顾和代码的整合
```deal_data.py```主要实现的功能就是读入一个fvqa的类似知识库的数据，然后对他里面的内容进行一个筛选，选取自己要的如head，tail，relation之类的内容，然后进行数据清洗，即answer filter，此时可以看到关系和实体的分布情况，并且显示统计结果，以及当前构建的知识库在三个数据集fvqa，okvqa，vqa2.0下的覆盖率，最后是将知识库存储为jsondl格式。<br>
## 接下来从三个子模块进行简单的分析，并介绍github中每个文件名的意义
1. ```get_new_all_json()```函数 <br>
读入一个fvqa的类似知识库的数据，然后对他里面的内容进行一个筛选，选取自己要的如head，tail，relation之类的内容,然后生成一个新的未经清洗的知识库 <br>
```all_fact_triples_release.json```  ---->  ```all_qs_dict_release_combine_all.json``` <br>
2. ```human_check()```函数 <br>
此函数进行数据清洗，human_check，洗掉脏数据等。 <br>
首先在answer_filter模块中，可以统计entity和relation的分布（按relation和entity出现次数从高到低排），生成```relation_all_sorted.json```和```entity_all_sorted.json```，同时取top100生成相应的分布图（plt）：```entity_first100.png```, ```relation_first100.png```。 <br>
上述四个生成的四个文件都整合在Data result distribution文件夹下 <br>
接下来输出统计的结果，包含了entity relation和triples的数量，以及当前知识库在三个数据集fvqa、vqa2.0、okvqa下的覆盖率，三个数据集的相关数据均在data文件夹下 <br>
```all_qs_dict_release_combine_all.json```  ----> ```json_afterclear.json``` <br>
3. ```convertjson2jsondl()```函数 <br>

