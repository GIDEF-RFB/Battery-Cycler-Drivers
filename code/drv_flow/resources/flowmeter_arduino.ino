#include <stdio.h>
const int pinNegativo = 2; // El pin digital donde está conectada la salida del caudalímetro del electrolito negativo.
const int pinPositivo = 7; // El pin digital donde está conectada la salida del caudalímetro del electrolito positivo.
// Digital pin used for auxiliar flowmeter
#define pinPositivo 7
#define pinNegativo 2

#define DEVICE_NUMBER 1
#define FIRMWARE_VERSION "2"
#define ENDING_CHARS "\n"
#define BAUDRATE 19200
#define MAX_BUFFER_SIZE 100
// #define K_FACTOR 1420.0
// K FACTOR en funcion del jet
// 17000.0 para el jet 1
// 7000.0 para el jet 2
// 3500.0 para el jet 3
// 2100.0 para el jet 4
// 1420.0 para no jet
bool led = 0;
int selected_k_factor = 0;
float K_FACTOR = 1420.0;
unsigned long tiempoAnterior = 0;
unsigned long intervalo = 1000000; // Intervalo en usegundos para calcular la frecuencia
volatile unsigned int contadorPulsosNegativo = 0;
volatile unsigned int contadorPulsosPositivo = 0;
float flow_pos = 0.0, flow_neg = 0.0;
char cadena[MAX_BUFFER_SIZE];
int indice = 0;


char REQ_INFO[] = ":IDN*?";
char REQ_MEAS[] = ":MEASure:FLOW?";
char SEND_INFO[] = "IDN:FLOWmeter";
char SEND_MEAS[] = "MEASure:FLOW:DATA:";
char SEND_ERROR[] = "SCPI:ERROR:";

void setup() {

  Serial.begin(BAUDRATE);

  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  pinMode(pinNegativo, INPUT_PULLUP);
  pinMode(pinPositivo, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(pinNegativo), contarPulsoNegativo, FALLING);
  attachInterrupt(digitalPinToInterrupt(pinPositivo), contarPulsoPositivo, FALLING);
}

void contarPulsoNegativo() {
  contadorPulsosNegativo++;
}

void contarPulsoPositivo() {
  contadorPulsosPositivo++;
}

void MEAS(char resultado[]) {
  char f_pos[20];
  char f_neg[20];
  // int len = snprintf(NULL, 0, "%f", flow_neg);
  // char *f_neg = malloc(len + 1);
  // snprintf(f_neg, len + 1, "%f", flow_neg);
  int aux_pos = flow_pos*1000;
  int aux_neg = flow_neg*1000;
  // Serial.print("Aux pos: ");Serial.println(aux_pos);
  // Serial.print("Aux neg: ");Serial.println(aux_neg);
  sprintf(f_pos, "%d", aux_pos);  // Convert flow_pos to string with 2 decimal places
  sprintf(f_neg, "%d", aux_neg);  // Convert flow_neg to string with 2 decimal places

  strcpy(resultado, SEND_MEAS);
  strcat(resultado, f_pos);
  strcat(resultado, ":");
  strcat(resultado, f_neg);
}

void INFO(char resultado[]) {
  char dev_num[3];
  char factor[3];
  sprintf(dev_num, "%03d", DEVICE_NUMBER);
  sprintf(factor, "%d",selected_k_factor);
  strcpy(resultado, SEND_INFO);
  strcat(resultado, ":k_factor:");
  strcat(resultado, factor);
  strcat(resultado, ":DEVice:");
  strcat(resultado, dev_num);
  strcat(resultado, ":VERsion:");
  strcat(resultado, FIRMWARE_VERSION);
}

void ERROR(char resultado[], char msg[]) {
  strcpy(resultado, SEND_ERROR);
  strcat(resultado, msg);
}

void process_scpi(void) {
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      char resultado[MAX_BUFFER_SIZE];
      char selec_k_factor[20]= "0";
      char *x = strchr(cadena, '_');
      if (x != NULL) {
        int index = x - cadena;
        strcpy(selec_k_factor, x + 1);
        strncpy(cadena, cadena, index);
        cadena[index] = '\0';
      }
      if (strcmp(cadena, REQ_MEAS) == 0) {
        MEAS(resultado);
      } else if (strcmp(cadena, REQ_INFO) == 0) {
        if (*selec_k_factor =='1'){
          K_FACTOR = 17000.0;
          selected_k_factor = 1;
        }
        else if (*selec_k_factor =='2'){
          K_FACTOR = 7000.0;
          selected_k_factor = 2;
        }
        else if (*selec_k_factor =='3'){
          K_FACTOR = 3500.0;
          selected_k_factor = 3;
        }else if (*selec_k_factor =='4'){
          K_FACTOR = 2100.0;
          selected_k_factor = 4;
        }else{
          K_FACTOR = 1420.0;
          selected_k_factor = 0;
        }
        INFO(resultado);
      } else {
        ERROR(resultado, cadena);
      }
      if (led == 0){
        digitalWrite(LED_BUILTIN, HIGH);
        led = 1;
      }else {
        digitalWrite(LED_BUILTIN, LOW);
        led = 0;
      }
      strcat(resultado, ENDING_CHARS);
      resultado[MAX_BUFFER_SIZE - 1] = '\0';
      Serial.print(resultado);
      indice = 0;
      memset(cadena, '\0', sizeof(cadena));
    } else {
      cadena[indice] = c;
      indice++;
    }
  }
}

void loop() {

  unsigned long tiempoActual = micros();
  // Serial.print("Tiempo actual:");Serial.println(tiempoActual);
  if (tiempoActual - tiempoAnterior >= intervalo) {
    unsigned int pulsosNegativo = contadorPulsosNegativo;
    unsigned int pulsosPositivo = contadorPulsosPositivo;
    // Serial.print("Pulsos negativos:");Serial.println(pulsosNegativo);
    contadorPulsosNegativo = 0;
    contadorPulsosPositivo = 0;
    tiempoAnterior = tiempoActual;
    flow_pos = pulsosPositivo*60/K_FACTOR;
    flow_neg = pulsosNegativo*60/K_FACTOR;
    // Serial.print("Caudal negativo: ");
    // Serial.print(flow_neg);
    // Serial.print(" l/min  ");
    // Serial.print("Caudal positivo: ");
    // Serial.print(flow_pos);
    // Serial.println(" l/min  ");
  }
  process_scpi();
}
