TARGET_NAME := dictcreator

UNIT := main mainWgt titledWgt
    
SRCDIR := src
INCDIR := src/include
OBJDIR := build

TPDEP := Qt5Widgets #three part dependencies

# ---

TARGET := $(TARGET_NAME)
OBJ := $(UNIT:%=%.o)
LIBS :=     $(shell pkg-config --libs $(TPDEP))
CFLAGS :=   $(shell pkg-config --cflags $(TPDEP)) -I$(INCDIR)
PREFIX ?= /usr/local

.PHONY: all clean

all : $(TARGET)

$(TARGET) : $(SUBBUILD) $(OBJ:%=$(OBJDIR)/%)
	$(CXX) -o $@ $^ $(LIBS)

$(OBJDIR)/%.o : $(SRCDIR)/%.cpp
	$(CXX) -o $@ -pedantic-errors -fPIC -c $< $(CFLAGS)

clean :
	$(RM) $(OBJ:%=$(OBJDIR)/%) $(TARGET)
