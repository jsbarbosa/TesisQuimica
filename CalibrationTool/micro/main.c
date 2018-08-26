#include "uart.h"
#include <util/delay.h>
#include <avr/interrupt.h>

#define STOP 0x01
#define START 0x02
#define SET_CHANNEL_0 0x03
#define SET_CHANNEL_1 0x04
#define SET_CHANNEL_2 0x05
#define SET_CHANNEL_3 0x06
#define NAME 0x0f

#define N_MEAN 10

void setupADC(void);
void setupUART(void);
void setChannel(uint8_t ch);
void sendADC(uint16_t value);

int main(void)
{
	setupADC();
	setupUART();

	uint8_t val, i;
	uint32_t mean;
	
	sei();

	while(1)
	{
		val = uart_getc();// & (0x7f);

		if(val == START)
		{
			mean = 0;
			for(i = 0; i < N_MEAN; i++)
			{
				ADCSRA |= (1 << ADSC); // start conversion
				while(ADCSRA & (1 << ADSC));
				mean += ADC;
			}
			sendADC(mean / N_MEAN);
		}
		else if(val == NAME)
		{
			uart_puts("Rutherford\n");
		}
		else if((val >= SET_CHANNEL_0) && (val <= SET_CHANNEL_3))
		{
			setChannel(val - SET_CHANNEL_0);
		}
		else
		{
			uart_putc(val);
		}
	}
	return 0;
}

void sendADC(uint16_t value)
{
	uint8_t high, low;
	high = (value >> 8) & (0x03);
	low = value;

	uart_putc(high);
	uart_putc(low);
}

void setChannel(uint8_t ch)
{
	uint8_t mask = ~((1 << MUX1) | (1 << MUX0));
	ADMUX = (ADMUX & mask) | ch;
}

void setupADC(void)
{
	/*setup ADC*/
	ADMUX |= (1 << REFS0); // internal reference
	//~ ADCSRA |= (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // set division factor to 128
	ADCSRA |= (1 << ADPS2) | (1 << ADPS1); // set division factor to 64
	//~ ADCSRA |= (1 << ADPS1) | (1 << ADPS0); // set division factor to 8
	ADCSRA |= (1 << ADEN);
}

void setupUART(void)
{
	PORTB &= ~(1 << UART_RX); // set low
	DDRB &= ~(1 << UART_RX); // input

	PORTB |= (1 << UART_TX); // set high
	DDRB |= (1 << UART_TX); // output
}
