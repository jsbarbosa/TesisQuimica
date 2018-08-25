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

#define EVERY_ADC 86

volatile uint8_t SKIP_ADC = 0;
volatile uint8_t RESET_INT0 = 0;

void setupADC(void);
void setupUART(void);
void setChannel(uint8_t ch);
void sendADC(uint16_t value);

ISR(ADC_vect)
{
	if(SKIP_ADC % EVERY_ADC == 0)
	{
		uint16_t value = ADC;
		sendADC(value);
	}
	SKIP_ADC += 1;
	ADCSRA |= (1 << ADSC);
}

ISR(INT0_vect)
{
	uint8_t val = uart_getc() & (0x7f);
	
	GIMSK &= ~(1 << INT0); // disable interrupt INT0
		
	if(val == START)
	{
		setupADC();
		ADCSRA |= (1 << ADEN) | (1 << ADSC); // adc enable and start conversion
	}
	else if(val == STOP)
	{
		ADCSRA &= ~(1 << ADEN);
	}
	else if(val == NAME)
	{
		uart_puts("Rutherford");
	}
	else if((val >= SET_CHANNEL_0) && (val <= SET_CHANNEL_3))
	{
		setChannel(val - SET_CHANNEL_0);
	}
	else
	{
		uart_putc(val);
	}
	RESET_INT0 = 1;
}

int main(void)
{	
	setChannel(1);
	
	setupUART();
	
	//~ MCUCR |= (1 << ISC01) | (1 << ISC00); // rising edge on INT0 // NO
	//~ MCUCR |= (1 << ISC01); // falling edge on INT0 // working first bytes
	MCUCR |= (1 << ISC00); // falling edge on INT0 
	GIMSK |= (1 << INT0); // enable interrupt INT0
	
	sei();
	
	DDRB |= (1 << PB4);
	
	while(1)
	{		
		if(RESET_INT0)
		{
			RESET_INT0 = 0;
			_delay_ms(100);
			GIFR |= (1 << INTF0);
			GIMSK |= (1 << INT0); // enable interrupt INT0
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
	ADCSRA |= (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // set division factor to 128
	ADCSRA |= (1 << ADATE)| (1 << ADIE); // auto trigger / enable interrupt
}

void setupUART(void)
{
	PORTB &= ~(1 << UART_RX); // set low
	DDRB &= ~(1 << UART_RX); // input
	
	PORTB |= (1 << UART_TX); // set high
	DDRB |= (1 << UART_TX); // output
}
