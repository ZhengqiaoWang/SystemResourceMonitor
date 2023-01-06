from pyecharts import charts
from pyecharts import options as opts
import os
import datetime


def exportCharts(process_name, data, output_path):
    page = charts.Page(
        layout=charts.Page.DraggablePageLayout)

    page.page_title = "{} 统计信息".format(process_name)
    line_cpu = charts.Line(
        opts.InitOpts(page_title="{} CPU占用(%)".format(process_name)))\
        .set_global_opts(title_opts=opts.TitleOpts(title="CPU占用信息", subtitle="单位: %"))
    line_cpu.add_xaxis(xaxis_data=data["Time"])
    line_cpu.add_yaxis("CPU占用(%)", y_axis=data["CPU"], markline_opts=opts.MarkLineOpts(
        data=[opts.MarkLineItem(type_="max"), opts.MarkLineItem(type_="average")]), label_opts=opts.LabelOpts(is_show=False))

    line_mem = charts.Line(
        opts.InitOpts(page_title="{} 内存占用(MB)".format(process_name)))\
        .set_global_opts(title_opts=opts.TitleOpts(title="内存占用信息", subtitle="单位: MB"))
    line_mem.add_xaxis(xaxis_data=data["Time"])
    line_mem.add_yaxis("内存(MB)", y_axis=data["MEM"], markline_opts=opts.MarkLineOpts(
        data=[opts.MarkLineItem(type_="max"), opts.MarkLineItem(type_="average")]), label_opts=opts.LabelOpts(is_show=False))

    line_io = charts.Line(
        opts.InitOpts(page_title="{} IO写(MB)".format(process_name)))\
        .set_global_opts(title_opts=opts.TitleOpts(title="IO信息", subtitle="单位: MB"))
    line_io.add_xaxis(xaxis_data=data["Time"])
    line_io.add_yaxis("IO写(MB)", y_axis=data["IO"], markline_opts=opts.MarkLineOpts(
        data=[opts.MarkLineItem(type_="max"), opts.MarkLineItem(type_="average")]), label_opts=opts.LabelOpts(is_show=False))

    page.add(line_cpu, line_mem, line_io)
    page.render(os.path.join(output_path, "{}.html".format(process_name)))


def export(data_dict: dict, output_path: str, interval):
    process_dat_path = os.path.join(output_path, "process")
    summury_txt_path = os.path.join(output_path, "summury.txt")

    os.makedirs(process_dat_path, exist_ok=True)

    # 统计信息
    close_process_set = set()  # 统计这个时间段内关闭的进程
    start_process_set = set()  # 统计这个时间段内开启的进程
    start_timestamp = datetime.datetime.now()
    stop_timestamp = datetime.datetime.now()

    for process_name, pm in data_dict.items():
        stat = pm.getStatistic()
        exportCharts(process_name, stat, process_dat_path)

        # 统计summury
        if(stat["END_TIME"] != None):
            close_process_set.add(process_name)

            if stop_timestamp < stat["END_TIME"]:
                stop_timestamp = stat["END_TIME"]

        # 统计开始结束时间
        if start_timestamp > stat["START_TIME"]:
            start_timestamp = stat["START_TIME"]

    for process_name, pm in data_dict.items():
        stat = pm.getStatistic()
        if start_timestamp + datetime.timedelta(milliseconds=interval) < stat["START_TIME"]:
            # 之后启动的
            start_process_set.add(process_name)

    with open(summury_txt_path, "w") as f:
        f.write("======== 汇总 ========\n")
        f.write("报告时间:{}\n".format(datetime.datetime.now()))
        f.write("统计时间段：{} - {}\n".format(start_timestamp, stop_timestamp))
        f.write("======== 打开进程({}个) ========\n".format(len(start_process_set)))
        for start_process in start_process_set:
            f.write(start_process + "\n")
        f.write("======== 关闭进程({}个) ========\n".format(len(close_process_set)))
        for close_process in close_process_set:
            f.write(close_process + "\n")
