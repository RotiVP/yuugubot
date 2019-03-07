#include "mainWgt.h"

MainWgt::MainWgt(QWidget *parent) : QMainWindow(parent)
{
	QStatusBar *statusBar = new QStatusBar;


	QComboBox *contextCB = new QComboBox;
	TitledWgt *contextCBT = new TitledWgt(contextCB, "Context");

	QComboBox *intentCB = new QComboBox;
	TitledWgt *intentCBT = new TitledWgt(intentCB, "Intent");

	QListView *exampleLV = new QListView;
	
	QGridLayout *viewLay = new QGridLayout;
	viewLay->addWidget(contextCBT, 0, 0, Qt::AlignTop | Qt::AlignHCenter);
	viewLay->addWidget(intentCBT, 1, 0, Qt::AlignTop | Qt::AlignHCenter);
	viewLay->setRowStretch(1, 1);
	viewLay->addWidget(exampleLV, 0, 1, 2, 1);


	QLineEdit *contextLE = new QLineEdit;
	TitledWgt *contextLET = new TitledWgt(contextLE, "Context");

	QLineEdit *intentLE = new QLineEdit;
	TitledWgt *intentLET = new TitledWgt(intentLE, "Intent");

	QLineEdit *exampleLE = new QLineEdit;
	TitledWgt *exampleLET = new TitledWgt(exampleLE, "Example");

	QPushButton *submit = new QPushButton("Submit");

	QGridLayout *editLay = new QGridLayout;
	editLay->addWidget(contextLET, 0, 0, Qt::AlignLeft | Qt::AlignVCenter);
	editLay->addWidget(intentLET, 0, 1, Qt::AlignLeft | Qt::AlignVCenter);
	editLay->setColumnStretch(1, 1);
	editLay->addWidget(exampleLET, 1, 0, 1, 2);
	editLay->addWidget(submit, 2, 0, 1, 2, Qt::AlignLeft | Qt::AlignVCenter);


	QVBoxLayout *mainLay = new QVBoxLayout;
	mainLay->setSizeConstraint(QLayout::SetMinimumSize);
	mainLay->addLayout(viewLay, 1);
	mainLay->addLayout(editLay, 0);

	QWidget *central = new QWidget;
	//central->setStyleSheet("QWidget {border: 1px solid black;}");
	central->setLayout(mainLay);

	this->setCentralWidget(central);
	this->setStatusBar(statusBar);
}
