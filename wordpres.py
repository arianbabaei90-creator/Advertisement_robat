import httpx
import config

async def wordpres(ads):
    url=f"{config.WP_URL}/wp-json/wp/v2/posts"
    try:
        async with httpx.AsyncClient(auth=(config.WP_USERNAME,config.WP_PASSWORD),
                                     timeout=15)as client:
            data={
                "title":ads["title"],
                "content":ads["description"],
                "status":"draft"
            }
            response=await client.post(url,json=data)
            if response.status_code==200:
                post=response.json()
                return True,post["id"]

            return False,f"http{response.status_code}:{response.text}"
    except httpx.RequestError as e:
        return False,f"error{e}"
    except (KeyError,TypeError) as e:
        return False,f"{e}"