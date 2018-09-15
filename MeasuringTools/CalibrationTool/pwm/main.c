#include <avr/interrupt.h>
#include <util/delay.h>
#include <stdio.h>

#define PORT PORTD
#define DDR DDRD
#define PIN PD6

#define FREQ 25.0f
//#define DELAY 1000 * (1 / FREQ) / 2
#define DELAY 1000 * (1 / FREQ)

ISR(TIMER0_OVF_vect)
{

}

void initTimer(void)
{
	TCCR0B |= (1 << CS00);
	TIMSK0 |= (1 << TOIE0);
}

int main(void)
{
	DDR |= (1 << PIN);
	//sei();

	while(1)
	{
		PORTD ^= (1 << PIN);
		_delay_ms(DELAY);
	}
	return 0;
}
