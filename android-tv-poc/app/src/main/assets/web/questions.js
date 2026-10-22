export const questions = await fetch('./questions.json').then(r=>{if(!r.ok)throw Error('Question data unavailable');return r.json()});
export const categories = ["Animals", "Arts & Humanities", "Brain Teasers", "Celebrities", "Entertainment", "General Knowledge", "Geography", "History", "Hobbies", "Kids Trivia", "Literature", "Movies", "Music", "People", "Science & Technology", "Sport", "Television", "Video Games", "World"];
export function questionPool(language,region){return language==='uk'&&region==='Europe'?questions:[];}
