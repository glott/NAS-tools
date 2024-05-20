from generate_ulid import gen_ulid

######## GENERATE SCRATCHPAD RULES ########
tem = """                        {
                            \"id\": \"%ID%\",
                            \"airportIds\": [
                                \"TPA\",
                                \"BOW\",
                                \"CLW\",
                                \"GIF\",
                                \"BKV\",
                                \"TPF\",
                                \"LAL\",
                                \"MCF\",
                                \"PIE\",
                                \"SRQ\",
                                \"VDF\",
                                \"VNC\",
                                \"SPG\",
                                \"PCM\",
                                \"ZPH\"
                            ],
                            \"searchPattern\": \"%PAT%\",
                            \"template\": \"%TEMP%\"
                        },"""
pat = ['LAL', 'YOJIX', 'DORMR#', 'DORMR', 'SIMMR', 'COVIA', 'PIE', 'DARBS', 'V97', 'SZW', 'GANDY#', 'GANDY', 'SABEE', 'RSW', 'SRQ', 'CROWD#', 'CROWD', 'PHK', 'PRICY#', 'PRICY', 'MINEE#', 'MINEE', 'BAYPO#', 'BAYPO', 'CAMJO', 'WILON', 'NITTS', 'OCF', 'GNV', 'TAY', 'ENDED#', 'ENDED', 'LACEN', 'MOMIE', 'CTY', 'KNEED', 'V152', 'T210', 'ORL', 'KNOST', 'JAX', 'WILON', 'OCF', 'RSW', 'CEXAN', 'SRQ']
rep = ['###A', '###A', '###B', '###B', '###B', '###B', '###B', '###D', '###D', '###D', '###F', '###F', '###F', '###F', '###F', '###H', '###H', '###H', '###M', '###M', '###M', '###M', '###N', '###N', '###N', '###N', '###N', '###N', '###N', '###N', '###U', '###U', '###U', '###U', '###U', '###R', '###R', '###R', '###R', '###W', '###X', '###X', '###X', '###Y', '###Y', '###Y']

for i in range(0, len(pat)):
    s = tem.replace('%ID%', str(gen_ulid()))
    s = s.replace('%PAT%', pat[i])
    s = s.replace('%TEMP%', rep[i])
    print(s)