/*
    Eduardo Meli 2023 - Funzione init custom per kafka_init

    Descrizione: Avvia il server tramite comando run.sh
    (incluso in bitnami/kafka) insieme ad uno script di
    creazione dei topic
*/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#define EXEC_WO_ARGS 1
#define EXEC_W_ARGS 3
#define DEFAULT_RUN_SCRIPT_PATH "/opt/bitnami/scripts/kafka/entrypoint.sh ./run.sh"
#define DEFAULT_INIT_SCRIPT_PATH "/opt/bitnami/scripts/kafka/init.sh"

inline void error(const char *what) { fprintf(stderr, "%s\n", what); }

int main(int argc, char **argv) {
  char *run_script_path = DEFAULT_RUN_SCRIPT_PATH;
  char *init_script_path = DEFAULT_INIT_SCRIPT_PATH;
  if (argc == 2)
    error("Utilizzo: init <run_path> <init_path>");
  if (argc == EXEC_W_ARGS) {
    run_script_path = argv[1];
    init_script_path = argv[2];
  }

  // system(run_script_path);
  if (!fork()) {
    system(run_script_path);
    return 0;
  } else {
    sleep(5);
    system(init_script_path);
  }
}