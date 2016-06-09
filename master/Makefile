CXX=g++
CXX_FLAGS=-std=c++14
LD_FLAGS=-lpthread -lwiringPi

all: master

%.o: %.cpp
	$(CXX) -c -o $@ $< $(CXX_FLAGS)

master: master.o
	$(CXX) -o $@ $^ $(LD_FLAGS)
