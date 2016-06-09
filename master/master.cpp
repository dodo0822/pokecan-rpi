#include <iostream>
#include <fstream>
#include <cstdio>
#include <ctime>
#include <thread>
#include <string>
#include <chrono>
#include <vector>

#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

#include <wiringPi.h>

#include "json.hpp"

#define BEEP

#define STR_MAX 1024

using json = nlohmann::json;

class Config {
public:
	int bin_height;
	int lift_height;
	int threshold;
	json route;

	Config() {}

	void load() {
		std::fstream fin("../config.json", std::fstream::in);
		json config = json::parse(fin);
		fin.close();
		bin_height = config["bin_height"];
		lift_height = config["lift_height"];
		threshold = config["threshold"];
		route = config["route"];
	}

	void save() {
		std::fstream fout("../config.json", std::fstream::out);
		json config;
		config["bin_height"] = bin_height;
		config["lift_height"] = lift_height;
		config["threshold"] = threshold;
		config["route"] = route;
		fout << config.dump();
		fout.close();
	}
};

class Status {
public:
	Status() : status(0), level(0), distance(0), requested(false) {}

	int status;
	int level;
	int distance;
	bool requested;
};

Config config;
Status status;
std::vector<int> motors(8, 0);

class CommThread {
public:
	CommThread() {}
	~CommThread() {
		stop_thread = true;
		if(thread.joinable()) thread.join();
	}

	void start() {
		stop_thread = false;
		thread = std::thread(&CommThread::thread_main, this);
	}

private:
	bool stop_thread;
	std::thread thread;
	void thread_main() {
		char *socket_path = "/tmp/pokecan.sock";
		struct sockaddr_un addr;
		char line[STR_MAX];
		int fd, cl, rc;

		fd = socket(AF_UNIX, SOCK_STREAM, 0);
		if(fd == -1) {
			perror("socket err");
			return;
		}

		memset(&addr, 0, sizeof(addr));
		addr.sun_family = AF_UNIX;
		strcpy(addr.sun_path, socket_path);
		unlink(socket_path);
		int len = strlen(addr.sun_path) + sizeof(addr.sun_family) + 1;

		if(bind(fd, (struct sockaddr*) &addr, len) == -1)	{
			perror("bind err");
			return;
		}

		if(listen(fd, 5) == -1) {
			perror("listen err");
			return;
		}

		while(!stop_thread) {
			cl = accept(fd, NULL, NULL);
			if(cl == -1) {
				perror("accept err");
				continue;
			}
			rc = read(cl, line, sizeof(line));
			if(rc == -1) {
				perror("read err");
			close(cl);
				continue;
			}
			std::string str(line, 0, rc);
			char resp[STR_MAX];

			try {
				auto req = json::parse(str);
				//printf("recv: %s\n", str.c_str());
				if(req["command"] == "status") {
					snprintf(resp, STR_MAX, "{\"status\":%d,\"level\":%d,\"distance\":%d,\"requested\":%s}", status.status, status.level, status.distance, (status.requested ? "true" : "false"));
				} else if(req["command"] == "dump_config") {
					snprintf(resp, STR_MAX, "{\"status\":\"ok\",\"bin_height\":%d,\"lift_height\":%d,\"threshold\":%d,\"route\":%s}", config.bin_height, config.lift_height, config.threshold, config.route.dump().c_str());
				} else if(req["command"] == "write_config") {
					bool ok = true;
					if(req["name"] == "bin_height") {
						config.bin_height = req["value"];
					} else if(req["name"] == "lift_height") {
						config.lift_height = req["value"];
					} else if(req["name"] == "threshold") {
						config.threshold = req["value"];
					} else if(req["name"] == "route") {
						config.route = req["value"];
					} else {
						ok = false;
						strncpy(resp, "{\"status\":\"error\",\"message\":\"invalid command\"}", STR_MAX);
					}

					if(ok) {
						config.save();
						strncpy(resp, "{\"status\":\"ok\"}", STR_MAX);
					}

				} else if(req["command"] == "stop_all_motors") {
					for(int i = 0; i < 8; ++i) {
						motors[i] = 0;
					}
				} else if(req["command"] == "motor") {
					if(!req["motor"].is_number() || !req["direction"].is_number()) {
						strncpy(resp, "{\"status\":\"error\",\"message\":\"invalid command\"}", STR_MAX);
					} else {
						int motor = req["motor"];
						int direction = req["direction"];
						if(!(motor >= 0 && motor <= 7)) {
							strncpy(resp, "{\"status\":\"error\",\"message\":\"invalid command\"}", STR_MAX);
						} else {
							if(direction == -1) {
								motors[motor] = -1;
							} else if(direction == 1) {
								motors[motor] = 1;
							} else {
								motors[motor] = 0;
							}
							strncpy(resp, "{\"status\":\"ok\"}", STR_MAX);
						}
					}
				} else if(req["command"] == "get_motors") {
					snprintf(resp, STR_MAX, "{\"status\":\"ok\",\"motors\":[%d,%d,%d,%d,%d,%d,%d,%d]}", motors[0], motors[1], motors[2], motors[3], motors[4], motors[5], motors[6], motors[7]);
				} else if(req["command"] == "proc_request") {
					status.requested = false;
					strncpy(resp, "{\"status\":\"ok\"}", STR_MAX);
				} else if(req["command"] == "set_request") {
					if(status.status != 0) {
						strncpy(resp, "{\"status\":\"error\",\"message\":\"not idle\"}", STR_MAX);
					} else {
						status.requested = true;
						strncpy(resp, "{\"status\":\"ok\"}", STR_MAX);
					}
				} else if(req["command"] == "set_status") {
					if(!req["status"].is_number()) {
						strncpy(resp, "{\"status\":\"error\",\"message\":\"invalid command\"}", STR_MAX);
					} else {
						int st = req["status"];
						if(st < 0 || st > 2) {
							strncpy(resp, "{\"status\":\"error\",\"message\":\"invalid command\"}", STR_MAX);
						} else {
							status.status = st;
							strncpy(resp, "{\"status\":\"ok\"}", STR_MAX);
						}
					}
				} else {
					strncpy(resp, "{\"status\":\"error\",\"message\":\"invalid command\"}", STR_MAX);
				}
			} catch(...) {
				strncpy(resp, "{\"status\":\"error\",\"message\":\"invalid request\"}", STR_MAX);
			}
			rc = write(cl, resp, strlen(resp));
			if(rc == -1) {
				perror("write err");
				close(cl);
				continue;
			}
			close(cl);
		}
	}
};

class SensorThread {
public:
	SensorThread() {}
	~SensorThread() {
		stop_thread = true;
		if(thread.joinable()) thread.join();
	}

	void start() {
		stop_thread = false;
		thread = std::thread(&SensorThread::thread_main, this);
	}

private:
	std::thread thread;
	bool stop_thread;
	int drop_count;

	int full_count;
	bool beep_on;

	void thread_main() {
		beep_on = false;
		drop_count = 0;
		digitalWrite(0, LOW);
		delay(100);
		while(!stop_thread) {
			digitalWrite(0, HIGH);
			delay(0.01);
			digitalWrite(0, LOW);
			
			long start = -1;
			long end = -1;

			while(digitalRead(2) == LOW) {
				start = micros();
			}

			while(digitalRead(2) == HIGH) {
				end = micros();
			}

			if(end == -1 || start == -1) {
				// Fail!
			} else {
				int duration = end - start;
				if(duration < 0) {
					puts("duration < 0");
					delay(100);
					continue;
				}
				int distance = (duration * 17150) / 1000000;
				int level = -1;
				status.distance = distance;
				printf("dist : %d\n", distance);
				if(distance > config.bin_height) level = 0;
				else level = 100 - ((distance * 100) / config.bin_height);
				if(level == 0 && status.level > 0) {
					if(drop_count < 3) drop_count++;
					else {
						drop_count = 0;
						status.level = 0;
					}
				} else {
					drop_count = 0;
					status.level = level;
				}

			}

			if(status.status == 0) {
				if(status.level > config.threshold) {
					full_count++;
#ifdef BEEP
					if(full_count % 2) {
						beep_on = true;
						digitalWrite(14, HIGH);
					} else {
						beep_on = false;
						digitalWrite(14, LOW);
					}
#endif
					if(full_count == 4) {
						printf("Requested!");
						status.requested = true;
						full_count = 0;
						if(beep_on) {
							digitalWrite(14, LOW);
							beep_on = false;
						}
						digitalWrite(14, LOW);
					}
				} else {
					if(beep_on) {
						digitalWrite(14, LOW);
						beep_on = false;
					}
					full_count = 0;
				}
			} else {
				if(beep_on) {
					digitalWrite(14, LOW);
					beep_on = false;
				}
				full_count = 0;
			}
			printf("FullCount=%d\n", full_count);
			delay(1000);
		}
	}
};

int main(int argc, char* argv[]) {
	wiringPiSetup();

	pinMode(0, OUTPUT);
	pinMode(2, INPUT);
	pinMode(14, OUTPUT);

	config.load();

	SensorThread worker;
	worker.start();

	CommThread comm;
	comm.start();

#ifdef BEEP
	for(int i = 0; i < 2; ++i) {
		digitalWrite(14, HIGH);
		std::this_thread::sleep_for(std::chrono::milliseconds(150));
		digitalWrite(14, LOW);
		std::this_thread::sleep_for(std::chrono::milliseconds(150));
	}
#endif

	while(true) {
		std::this_thread::sleep_for(std::chrono::milliseconds(10000));
	}

	return 0;
}
