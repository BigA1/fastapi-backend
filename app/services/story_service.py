from app.supabase.client import supabase
from app.models.story import StoryCreate

def get_all_stories(user_id: str):
    return supabase.table("stories").select("*").eq("user_id", user_id).execute().data

def get_story_by_id(story_id: int):
    result = supabase.table("stories").select("*").eq("id", story_id).single().execute()
    return result.data

def create_story(story: StoryCreate, user_id: str):
    data = story.dict()
    data["user_id"] = user_id
    return supabase.table("stories").insert(data).execute().data

def update_story(story_id: int, story: StoryCreate):
    data = story.dict()
    return supabase.table("stories").update(data).eq("id", story_id).execute().data

def delete_story(story_id: int):
    return supabase.table("stories").delete().eq("id", story_id).execute().data
