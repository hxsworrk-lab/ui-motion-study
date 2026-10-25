# Spoken-word level preparation

A self-initiated 36-second technical study by Hx Works, not a client commission or Hx Works narration.

## Files

- source-english.ogg: unchanged source recording.
- prepared-english.wav: 60 Hz high-pass filtering and two-pass loudness normalization; 48 kHz, mono, PCM24 export.
- measurements.json: final-file measurements and hashes.
- index.html: original/prepared playback, exact scope and attribution.

No words, breaths or pauses were removed or rearranged. The study does not demonstrate denoising, detailed dialogue editing, long-form consistency, ACX compliance or buyer acceptance. Final-file technical measurements and browser playback are not listening-quality acceptance.

## Attribution and audio license

“Recording of speaker of British English (Received Pronunciation)” — P. Roach / International Phonetic Association. Speaker unnamed on the source page. Copyright International Phonetic Association.

Source: https://commons.wikimedia.org/wiki/File:Recording_of_speaker_of_British_English_(Received_Pronunciation).ogg

The original and adapted audio are distributed under **CC BY-SA 3.0 Unported**: https://creativecommons.org/licenses/by-sa/3.0/

Changes by Hx Works: 60 Hz high-pass filter, two-pass loudness normalization, resampling to 48 kHz, 24-bit PCM export, and attribution metadata. No endorsement is implied. Adaptations of the audio must comply with the license, including attribution and ShareAlike.

## Reproduction record

FFmpeg N-92722-gf22fcd4483 (existing installed build). After the high-pass filter and resampling, first-pass measured values were I=-20.44, LRA=4.90, TP=0.01, threshold=-31.02 and offset=0.36. Second-pass filter:

    highpass=f=60,aformat=sample_rates=48000:channel_layouts=mono,loudnorm=I=-19:LRA=11:TP=-2.5:measured_I=-20.44:measured_LRA=4.90:measured_TP=0.01:measured_thresh=-31.02:offset=0.36:linear=true:print_format=json

The measured-input constraints selected dynamic normalization. Independently analyzing the final exported WAV reports I=-19.21 LUFS, TP=-2.50 dBTP and LRA=4.10 LU; these final-file values take precedence over in-filter output estimates. Sample peak is approximately -2.49989 dBFS; rounded true peak values are not an infinite-precision guarantee.

Chosen targets are study settings, not a client delivery specification. The original was retained unchanged; duration differs by about 3.26 microseconds due to sample-count rounding during resampling.
