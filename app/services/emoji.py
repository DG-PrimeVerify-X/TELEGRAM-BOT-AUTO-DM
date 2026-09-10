from aiogram.types import MessageEntity

def custom_emoji_entity(custom_id:str, fallback:str):
    return (fallback,[MessageEntity(type="custom_emoji",offset=0,length=len(fallback.encode("utf-16-le"))//2,custom_emoji_id=custom_id)])
