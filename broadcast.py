import asyncio

import hoshino
from hoshino.service import sucmd
from hoshino.typing import CommandSession, CQHttpError
from hoshino.service import Service

#格式：bc/广播 服务名 广播内容
@sucmd('broadcast', aliases=('bc', '广播'))
async def broadcast(session: CommandSession):
    msg = session.current_arg
    if not ' ' in msg:
        await session.send(f'请输入服务名，全群广播则输入all')
        return
    args = msg.split(' ',1)
    bc_sv_name =  args[0]
    bc_msg = args[1]
    svs = Service.get_loaded_services()
    if bc_sv_name not in svs and bc_sv_name != 'all':
        await session.send(f'未找到该服务，请输入正确的服务')
        return
    sid = list(hoshino.get_self_ids())[0]
    if bc_sv_name == 'all':
        gl = await session.bot.get_group_list(self_id=sid)
        gl = [ g['group_id'] for g in gl ]
    else:
        enable_groups = await svs[bc_sv_name].get_enable_groups()
        gl = enable_groups.keys()
    for sid in hoshino.get_self_ids():
        for g in gl:
            await asyncio.sleep(0.5)
            try:
                await session.bot.send_group_msg(self_id=sid, group_id=g, message=bc_msg)
                hoshino.logger.info(f'群{g} 投递广播成功')
            except Exception as e:
                hoshino.logger.error(f'群{g} 投递广播失败：{type(e)}')
                try:
                    await session.send(f'群{g} 投递广播失败：{type(e)}')
                except Exception as e:
                    hoshino.logger.critical(f'向广播发起者进行错误回报时发生错误：{type(e)}')
    await session.send(f'广播完成！')
