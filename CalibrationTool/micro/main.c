#include "uart.h"
#include <util/delay.h>
#include <avr/interrupt.h>

#define STOP 0x01
#define START 0x02

volatile uint8_t RESET_INT0 = 0;

void setupADC(void);
void setChannel(uint8_t ch);

ISR(ADC_vect)
{
	uint16_t value = ADC;
	char chars[2];
	chars[0] = value >> 8;
	chars[1] = value;
	
	uart_puts(chars);
	
	ADCSRA |= (1 << ADSC);
}

ISR(INT0_vect)
{
	uint8_t val = uart_getc() & (0x0f);
	
	GIMSK &= ~(1 << INT0); // disable interrupt INT0
		
	if(val == START)
	{
		ADCSRA |= (1 << ADEN) | (1 << ADSC); // adc enable and start conversion
	}
	else if(val == STOP)
	{
		ADCSRA &= ~(1 << ADEN);
	}
	else
	{	
		_delay_ms(100);
		uart_putc(val);
	}
	RESET_INT0 = 1;
}

int main(void)
{	
	setupADC();
	setChannel(1);
	
	//~ MCUCR |= (1 << ISC01) | (1 << ISC00); // rising edge on INT0
	MCUCR |= (1 << ISC01); // falling edge on INT0
	GIMSK |= (1 << INT0); // enable interrupt INT0
	
	sei();
	
	DDRB |= (1 << PB4);
	PORTB |= (1 << UART_RX) | (1 << UART_TX); // pull up
	
	while(1)
	{
		PORTB ^= (1 << PB4);
		_delay_ms(500);
		
		if(RESET_INT0)
		{
			RESET_INT0 = 0;
			GIFR |= (1 << INTF0);
			GIMSK |= (1 << INT0); // enable interrupt INT0
		}
	}
	return 0;
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
	ADCSRA |= (1 << ADPS2) | (1 << ADPS1); // set division factor to 64
	ADCSRA |= (1 << ADIE); // enable interrupt
}
