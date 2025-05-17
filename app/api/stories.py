from fastapi import APIRouter, HTTPException, Depends
from app.models.story import Story, StoryCreate
from app.services import story_service
from app.auth.dependencies import verify_token

router = APIRouter(prefix="/stories", tags=["stories"])

@router.get("/", response_model=list[Story])
def list_stories(user=Depends(verify_token)):
    return story_service.get_all_stories(user_id=user["sub"])

@router.get("/{story_id}", response_model=Story)
def get_story(story_id: int, user=Depends(verify_token)):
    story = story_service.get_story_by_id(story_id)
    if not story or story["user_id"] != user["sub"]:
        raise HTTPException(status_code=404, detail="Story not found")
    return story

@router.post("/", status_code=201, response_model=Story)
def create(story: StoryCreate, user=Depends(verify_token)):
    return story_service.create_story(story, user_id=user["sub"])[0]

@router.put("/{story_id}", response_model=Story)
def update(story_id: int, story: StoryCreate, user=Depends(verify_token)):
    existing = story_service.get_story_by_id(story_id)
    if not existing or existing["user_id"] != user["sub"]:
        raise HTTPException(status_code=404, detail="Story not found")
    return story_service.update_story(story_id, story)[0]

@router.delete("/{story_id}", status_code=204)
def delete(story_id: int, user=Depends(verify_token)):
    existing = story_service.get_story_by_id(story_id)
    if not existing or existing["user_id"] != user["sub"]:
        raise HTTPException(status_code=404, detail="Story not found")
    story_service.delete_story(story_id)
