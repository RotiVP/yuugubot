#include "titledWgt.h"

TitledWgt::TitledWgt(QWidget *widget, const QString& title, QWidget *parent) : QWidget(parent)
{
	QLabel *titleLbl = new QLabel(title);

	QVBoxLayout *layout = new QVBoxLayout;
	layout->addWidget(titleLbl, 0, Qt::AlignCenter);
	layout->addWidget(widget);

	this->setLayout(layout);
}
