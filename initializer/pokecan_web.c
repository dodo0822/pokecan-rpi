#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void daemon_main() {
	chdir("/home/pi/Pokecan/web");
	execlp("/usr/bin/node", "node", "server.js");
}

int main(int argc, char* argv[]) {
	pid_t pid = 0;
	pid_t sid = 0;
	pid_t pid2 = 0;
	int status;

	pid = fork();

	if(pid < 0) {
		puts("first fork failed!");
		exit(1);
	} else if(pid > 0) {
		waitpid(pid, &status, NULL);
		exit(0);
	} else {
		umask(0);
		sid = setsid();

		if(sid < 0) {
			puts("set session id failed!");
			exit(1);
		}

		chdir("/");

		pid2 = fork();
		
		if(pid2 < 0) {
			puts("second fork failed!");
			exit(1);
		} else if(pid2 > 0) {
			exit(0);
		} else {
			daemon_main();
		}
	}
}
