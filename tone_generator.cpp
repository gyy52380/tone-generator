#include <stdio.h>
#include <math.h>
constexpr double M_2_PI = 3.14159265358979323846 * 2;

#include "typedef.h"

#define LK_REGION_IMPLEMENTATION
#include "lk_region.h"
LK_Region temporary_memory = {};
constexpr LK_Region *temp = &temporary_memory;


struct LK_Wave
{
    i16 *samples;
    u32 count;
    u32 channels;
    u32 frequency;
};

void output_wave_file(const char* path, LK_Wave sound)
{
    FILE* out = fopen(path, "wb");
    if (!out)
    {
        printf("Couldn't open file %s for writing!\n", path);
        return;
    }

    #define Write(from, size) \
        if (fwrite(from, size, 1, out) != 1) \
        { \
            printf("Couldn't write to file %s!\n", path); \
            fclose(out); \
            return; \
        }

    #define Write16(value) { u16 v = value; Write(&v, 2) }
    #define Write32(value) { u32 v = value; Write(&v, 4) }

    constexpr u32 RIFF = 0x46464952; // "RIFF" big-endian
    constexpr u32 WAVE = 0x45564157; // "WAVE" big-endian
    constexpr u32 FMT  = 0x20746D66; // "fmt " big-endian
    constexpr u32 DATA = 0x61746164; // "data" big-endian
    constexpr u32 PCM  = 1;

    int data_size = sound.count * sound.channels * 2;

    // RIFF chunk
    Write32(RIFF);
    Write32(data_size + 36);
    Write32(WAVE);

    // fmt chunk
    Write32(FMT);
    Write32(16);
    Write16(PCM);
    Write16(sound.channels);
    Write32(sound.frequency);
    Write32(sound.frequency * sound.channels * 2);
    Write16(sound.channels * 2);
    Write16(16);

    // data chunk
    Write32(DATA);
    Write32(data_size);

    Write(sound.samples, data_size);

    fclose(out);

    #undef Write
    #undef Write16
    #undef Write32
}

void output_text_file(const char* path, LK_Wave sound)
{
	FILE* out = fopen(path, "wt");
    if (!out)
    {
        printf("Couldn't open file %s for writing!\n", path);
        return;
    }

    for (int i = 0; i < sound.count; i++)
    {
    	if (fprintf(out, "%hd\n", sound.samples[i]) < 0)
    	{
    		fclose(out);
    		return;
    	}
    }

    fclose(out);
}

// FREQUENCY = SAMPLES/SEC
constexpr u32 FREQUENCY = 200;

LK_Wave generate_sine_tone(float tone_frequency_hz, u32 duration_ms, u32 frequency = FREQUENCY) //frequency should be >= 1000
{
	const u32 sample_count = duration_ms / 1000.f * frequency;
	const double dt = 1.0f / frequency;

	i16 *samples = LK_RegionArray(temp, i16, sample_count);

	for (int i = 0; i < sample_count; i++)
	{
		float temp_amplitude = sin(M_2_PI * tone_frequency_hz * i*dt);
		i16 amplitude = (i16)(temp_amplitude * 32767);

		samples[i] = amplitude;
	}

	LK_Wave result;
	result.samples 		= samples;
	result.count 		= sample_count;
	result.channels 	= 1;
	result.frequency 	= frequency;

	return result;
}

LK_Wave generate_sine_tone_with_ad(float tone_frequency_hz, float duration_s, float attack_duration_s, float decay_duration_s, u32 frequency = FREQUENCY) //frequency should be >= 1000
{
	const u32 sample_count = duration_s * frequency;
	const float dt = 1.0f / frequency;


	i16 *samples = LK_RegionArray(temp, i16, sample_count);

	for (int i = 0; i < sample_count; i++)
	{
		float t = i * dt; // time passed in seconds

		float temp_amplitude = sin(M_2_PI * tone_frequency_hz * t);

		if (t < attack_duration_s)
		{
			float factor = t / attack_duration_s ;
			//factor = 1/fabs(logf(factor)/logf(10)) / 10;
			temp_amplitude *= factor;
		}
		else if (t > duration_s - decay_duration_s)
		{
			float temp_t = t - (duration_s - decay_duration_s); // offset t to 'zero'
			float factor = 1.0f - (temp_t / decay_duration_s);  // lower sound from 1 to 0
			//factor = 1/fabs(logf(factor)/logf(10)) / 10;
			temp_amplitude *= factor;
		}	

		i16 amplitude = (i16)(temp_amplitude * 32767);

		samples[i] = amplitude;
	}

	LK_Wave result;
	result.samples 		= samples;
	result.count 		= sample_count;
	result.channels 	= 1;
	result.frequency 	= frequency;

	return result;
}


int main(int argc, const char **argv)
{
	LK_Wave long_sine 	= generate_sine_tone_with_ad(440, 8, 2, 2.5);
	LK_Wave short_sine 	= generate_sine_tone_with_ad(440, 0.25, 0.1, 0.11);

	output_wave_file("output/long_sine.wav", long_sine);
	output_wave_file("output/short_sine.wav", short_sine);

	output_text_file("output/long_sine.txt", long_sine);

	return 0;
}