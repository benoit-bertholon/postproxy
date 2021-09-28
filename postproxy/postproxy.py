from aiohttp import web
import aiohttp
import asyncio
import datetime
from domonic.dom import *
from domonic import html, div, span, form, table, tr,  td, input as input_, button, body, head, style, script, label, link, h1

memory = {"relay":"","lines":[], "websockets":[]}


script_ws = """
    if ("WebSocket" in window) {
            var ws = new WebSocket('ws://' + window.location.host + '/ws');
             console.log(ws);
            ws.onmessage = function (event) {
                 console.log(event);
                if(event.data == "refresh")
                window.location.reload()
            }
        }"""


async def handle(request):
    print(memory)
    relay = request.query.get('relay')
    if relay is not None:
        memory["relay"]=relay
    replay_id = request.query.get('replay_id')
    if replay_id is not None:
        await send_replay(int(replay_id))
        
    myform = form(_action="/", _method="get")
    myform.appendChild(div(label("replay to server: "),
                           input_( memory["relay"], _type="text", _name="relay", _value=memory["relay"]),
                           _class="form-group"
                           ))
    myform.appendChild(button( "Config", _type="submit", _class="btn btn-primary"))
    
    mytable = table(tr(td("Time"),td("DATA"),td()), _class="table")
    for i,l in reversed(list(enumerate(memory["lines"]))):
        mytable.appendChild(tr(td(l["time"]),td(l["data"], td(
        form(input_(_type="hidden",_name="replay_id",_value="%d"%i),button( "Replay", _type="submit", _class="btn btn-primary"),_action="/", _method="get"
        )
        ))))

    site = html(
          head(
              link(_href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css", _rel="stylesheet"),
              
          ),
          body(
            div(
              h1("Replay Post Server"),
              myform,
              mytable,
              script(_src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.1/dist/js/bootstrap.min.js"),
              _class="container"
              ),
              script(script_ws)
            )
          )
    return web.Response(body=str(site), headers={'Content-Type': 'text/html'})
    
   
import random
async def handle_post(request):
    
    memory["lines"].append({"time":datetime.datetime.now().isoformat() , "data":await request.text()})
    for _ws in memory['websockets']:
        print(_ws)
        await _ws.send_str('refresh')
    await send_replay(len(memory["lines"])-1)
    return web.Response(text="toto")

async def send_replay(replay_id):
    print("send replay", replay_id)
    async with aiohttp.ClientSession() as session:
        async with session.post(memory["relay"], data=memory["lines"][replay_id]["data"]) as response:
            pass

class WebSocket(web.View):
    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)
        memory['websockets'].append(ws)
        async for msg in ws:
            if msg.tp == MsgType.text:
                if msg.data == 'close':
                    await ws.close()
                else:
                    print(msg)
            elif msg.tp == MsgType.error:
                log.debug('ws connection closed with exception %s' % ws.exception())
        memory['websockets'].remove(ws)
        return ws

app = web.Application( )
app.add_routes([web.get('/', handle),
                web.get('/ws', WebSocket),
                web.post('/', handle_post)])

def main():
    import sys
    port = 8899
    if len(sys.argv)>1:
        try :
            port= int(sys.argv[1])
        except ValueError:
            print("cannot parse %s as interger"%sys.args[1])
    web.run_app(app, port=port)



if __name__ == '__main__':
    main()
