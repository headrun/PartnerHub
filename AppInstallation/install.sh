#! /bin/sh

common_pkgs="vim python3.6 python3-pip cron nginx"
python_pkgs="scrapy==1.8.0 Flask==1.1.1 requests Flask-RESTful==0.3.8 uwsgi==2.0.18" 

apt_install() {
    sudo apt-get install $1
}

pip_install() {
    sudo pip3 install $1
}

lockrun() {
    file="lockrun.c"
    if [ -f $file ] ; then
        rm $file
    fi
    binpath="/usr/local/bin/"
    URL="http://www.unixwiz.net/tools/$file"
    wget "${URL}"
    cc ${file} -o lockrun
    sudo cp lockrun ${binpath}
    rm $file
    rm lockrun
}

main() {
        apt_install "$common_pkgs"
        lockrun
        pip_install "$python_pkgs"
}

main

