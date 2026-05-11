import asyncio
import logging
import httpx
import math

logger = logging.getLogger(__name__)
async def fetch_schedule(teacher_name, week_number):
    url = f"https://t2.iti-khsu.ru/api/getpairsweek?type=teacher&data={teacher_name}&week={week_number}"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                data['week_number'] = week_number
                return data
            else:
                print(f"HTTP {response.status_code} for week {week_number}")
                return None
    except httpx.TimeoutException:
        logger.error(f"Error while fetching schedule for {teacher_name} in {week_number}")
        return None
    except Exception as e:
        print(e)
        return None

async def get_teacher_schedule(teacher: str, month: int):
    teacher = teacher.strip()
    
    weeks_count = math.ceil(month * 30 / 7)
    start_week = weeks_count - 4
    weeks = list(range(start_week, start_week + 5))
    
    print(f"Weeks: {weeks}")
    tasks = [fetch_schedule(teacher, week) for week in weeks]
    results = await asyncio.gather(*tasks)
    successful_results = [r for r in results if r is not None]
    return successful_results
    '''
    if results:
        filename = f"{teacher}_{calendar.month_name[month]}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Saved: {filename} ({len(results)}/{len(weeks)} weeks)")
    '''
