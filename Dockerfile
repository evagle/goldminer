FROM ubuntu

ENV DEBIAN_FRONTEND noninteractive

# set apt-get source to aliyun
RUN  sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN  apt-get clean
RUN apt-get update

RUN apt-get install -y apt-utils

# install python3.6 and pip3
RUN apt-get install -y python3.6
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 100
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 100
RUN apt-get install -y python3-pip
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 100

RUN apt-get install -y vim curl

# install ta-lib from source code
RUN curl https://jaist.dl.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz -o /tmp/ta-lib.tar.gz
RUN cd /tmp && tar -xzvf /tmp/ta-lib.tar.gz
RUN cd /tmp/ta-lib && ./configure --prefix=/usr && make && make install
RUN rm -r /tmp/ta-lib*

# install zh language support
RUN apt-get install -y language-pack-zh-hans
ENV LANG zh_CN.UTF-8
ENV LANGUAGE zh_CN:zh
ENV LC_ALL zh_CN.UTF-8

# install python dependencies for goldminer
RUN pip install numpy pandas -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install pymysql sqlalchemy -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install xlrd lxml requests bs4 -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install tushare gm -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install TA-Lib -i https://mirrors.aliyun.com/pypi/simple/

# clean image
RUN apt-get clean
RUN apt-get autoremove

CMD ["/bin/bash"]
