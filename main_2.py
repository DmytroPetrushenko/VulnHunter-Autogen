from utils.msf.data_compressor import DataCompressor

messages = """
RHOSTS => 63.251.228.70
THREADS => 50
[*]  TCP UNFILTERED 63.251.228.70:1
[*]  TCP UNFILTERED 63.251.228.70:2
[*]  TCP UNFILTERED 63.251.228.70:3
[*]  TCP UNFILTERED 63.251.228.70:5
[*]  TCP UNFILTERED 63.251.228.70:6
[*]  TCP UNFILTERED 63.251.228.70:8
[*]  TCP UNFILTERED 63.251.228.70:9992
[*]  TCP UNFILTERED 63.251.228.70:9995
[*]  TCP UNFILTERED 63.251.228.70:9997
[*]  TCP UNFILTERED 63.251.228.70:9998
[*]  TCP UNFILTERED 63.251.228.70:9999
[*] Scanned 1 of 1 hosts (100% complete)
[*] Auxiliary module execution completed
"""

compressor = DataCompressor()
compressor.start_compressing(messages)

# for key, value in compressor.result_dict.items():
#     print(f"{key}: {value}")

print(compressor.get_compressed_output())
