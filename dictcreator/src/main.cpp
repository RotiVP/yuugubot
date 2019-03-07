#include <QApplication>

#include <cmath>

#include "mainWgt.h"

int main(int argc, char **argv)
{
    //QApplication::setAttribute(Qt::AA_EnableHighDpiScaling);
    
    QApplication qapp(argc, argv);

    MainWgt mwgt;
    mwgt.show();

    return qapp.exec();
}
