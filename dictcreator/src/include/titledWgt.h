#ifndef TITLEDWGT_H
#define TITLEDWGT_H

#include <QLabel>
#include <QVBoxLayout>

class TitledWgt : public QWidget {
public:
	TitledWgt(QWidget *widget, const QString& title, QWidget *parent = 0);
};

#endif
