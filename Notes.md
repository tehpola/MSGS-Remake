# Mike Slegeir's Gnar Skata Remake

## Intentions

1. Make a simple game
2. Work with familiar tech
3. Create something small in scope
4. Don't get caught up in analysis paralysis
5. Rekindle the joy and excitement in game development

## Approach

1. Recreate the original MSGS using the original art
    - [x] Choose a technology that matches the original engine's complexity: pygame
    - [x] Get an animated player character using the original sprites
    - [x] Import the original backgrounds and geometry
    - [x] Implement basic physics
    - [x] Reset the player to the start when reaching the end or falling
    - [x] Create a simple level editor
    - [x] Implement multiple, looping environments
    - [ ] Following the original control scheme, implement flip tricks
    - [ ] Following the original control scheme, implement grinds
    - [ ] Implement hazards that will cause the player to drop to its death
    - [ ] Track and display combos and points
2. Reimagine the original using new art and more advanced features
   - [ ] Extend the character sheet to include a broader suite of tricks
   - [ ] Using live action video - possibly fed through Stable Diffusion, create a new character
   - [ ] Implement scrolling / parallax environments
   - [ ] Implement banks
   - [ ] Implement radial transition
   - [ ] Integrate facial / emotional tracking to guide the player character's performance

## Notes

### Level Editor

- `EditorGeo` objects are live, but should update the `Environment`'s `geo` for serialization