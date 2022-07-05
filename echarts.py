# 导入要使用的模块
from pyecharts import options as opts
from pyecharts.charts import Bar, Grid, Line, Liquid, Page, Pie
from pyecharts.commons.utils import JsCode
from pyecharts.components import Table
from pyecharts.faker import Faker
from pyecharts.globals import ThemeType

import pymysql

# 连接数据库
db = pymysql.connect(host='localhost', user='root', passwd='f173486', port=3307, db='shuju')

# 开启一个游标cursor
cursor = db.cursor()

# 获取student数据表里的所有数据
sql = 'select * from Sheet1'

# 执行sql中的语句
cursor.execute(sql)

# 将获取到的sql数据全部显示出来
result = cursor.fetchall()

# 定义需要用上的空数据数组，然后通过遍历数据库的数据将数据附上去
name = []
score = []
director = []
actor = []
year = []
type = []
time = []
language = []
comment = []
area = []
# 遍历表里的数据
for i in range(1, len(result)):
    name.append(result[i][0])
    score.append(float(result[i][1]))
    director.append(result[i][2])
    actor.append(result[i][3])
    year.append(result[i][4])
    type.append(result[i][5])
    time.append(int(result[i][6]))
    language.append(result[i][7])
    comment.append(int(result[i][8])/1e5)
    area.append(result[i][9])

# 剔除异常数据
for i in range(len(time)):
    if i == len(time)-1:
        break
    if int(time[i]) < 30 or int(time[i]) > 300:
        del time[i]
        del score[i]

# 创建三个关系的字典，为了后面排序使用
time_score = {}
score_comment = {}
year_numbers = {}
for i in range(len(time)):
    if time[i] < 30:
        continue
    else:
        # 创建时长和分数关系，用字典保存{“time”：score}
        time_score[time[i]] = score[i]
        # 创建评分和评论数关系
        if score[i] not in score_comment:
            score_comment[score[i]] = comment[i]
        # 创建年份和电影数量关系
        if int(year[i]) in year_numbers:
            year_numbers[int(year[i])] += 1
        else:
            year_numbers[int(year[i])] = 1

# 将每个图 封装到 函数
# 1.条形图

# 排序后重新添加，按照时长排序（time）
time_score = sorted(time_score.items(), key=lambda x:x[0])
time1 = []
score1 = []
# 添加排序后的数据
for i in range(len(time_score)):
    time1.append(time_score[i][0])
    score1.append(time_score[i][1])

# 创建条形图
def bar_datazoom_slider() -> Bar:
    c = (

        Bar(init_opts=opts.InitOpts(theme=ThemeType.MACARONS))
            .add_xaxis(time1[:50])
            .add_yaxis("评分", score1[:50])
            .set_global_opts(
            title_opts=opts.TitleOpts(title="时长-评分"), # 标题
            datazoom_opts=[opts.DataZoomOpts()],
        )

    )
    return c


# 2.带标记点的折线图
# 按照年份排序
year_numbers = sorted(year_numbers.items(), key=lambda x:x[0])
year2 = []
numbers2 = []
# 添加排序后的数据
for i in range(len(year_numbers)):
    year2.append(str(year_numbers[i][0]))
    numbers2.append(year_numbers[i][1])


def line_markpoint() -> Line:
    c = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.MACARONS))
            # 创建年份-电影数量折线图
            .add_xaxis(year2[70:88]) # 年份
            .add_yaxis(
            "评论数",
            comment[70:88],
            markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max")]),
        )
            # 创建年份-评论数折线图
            .add_yaxis(
            "电影数",
            numbers2[70:88],
            markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="min")]),
        )
            .set_global_opts(title_opts=opts.TitleOpts(title="年份-数量-评论数"))
    )
    return c


# 3.玫瑰型饼图
def pie_rosetype() -> Pie:
    c = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.MACARONS))

            # 创建电影类型-评论数饼形图
            .add(
            "",
            [list(z) for z in zip(type[:50], comment[:50])],
            radius=["30%", "75%"],
            center=["25%", "50%"],
            rosetype="radius",
            label_opts=opts.LabelOpts(is_show=False),
        )
            # 创建电影类型-评分饼形图
            .add(
            "",
            [list(z) for z in zip(type[:50], score[:50])],
            radius=["30%", "75%"],
            center=["75%", "50%"],
            rosetype="area",
        )
            .set_global_opts(title_opts=opts.TitleOpts(title="类型-评分-评论数")) # 标题
    )
    return c


# 表格
def table_base() -> Table:
    table = Table()
    # 创建表头
    headers = ["File name", "Score", "Year", "Time", "Language", "Comment", "Area"]
    rows = []
    for i in range(1,10):
        rows.append([result[i][0],result[i][1],result[i][4],result[i][6],result[i][7],result[i][8],result[i][9]])

    # 放入rows数据
    table.add(headers, rows).set_global_opts(
        title_opts=opts.ComponentTitleOpts(title="Table") # 标题
    )
    return table


def page_simple_layout():
    page = Page(page_title="豆瓣电影数据分析可视化",layout=Page.SimplePageLayout) #  默认布局
    # page = Page(layout=Page.SimplePageLayout)  # 简单布局
    # 将上面定义好的图添加到 page
    page.add(
        bar_datazoom_slider(),
        line_markpoint(),
        pie_rosetype(),
        table_base(),
    )
    page.render("豆瓣电影数据分析可视化.html")


if __name__ == "__main__":
    page_simple_layout()

# def page_simple_layout():
#     page = Page(layout=Page.DraggablePageLayout)
#     # 将上面定义好的图添加到 page
#     page.add(
#         bar_datazoom_slider(),
#         line_markpoint(),
#         pie_rosetype(),
#         table_base(),
#     )
#     page.render("page_simple_layout.html")

