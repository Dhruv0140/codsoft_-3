from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)

# Function to load pickled data with error handling
def load_pickle(filename):
    try:
        with open(filename, 'rb') as file:
            return pickle.load(file)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

# Load data
popular_df = load_pickle('popular.pkl')
pt = load_pickle('pt.pkl')
books = load_pickle('books.pkl')
similarity_scores = load_pickle('similarity_scores.pkl')

# Ensure data was loaded successfully
if any(data is None for data in [popular_df, pt, books, similarity_scores]):
    raise RuntimeError("Failed to load one or more pickle files. Check error messages above.")

@app.route('/')
def index():
    if popular_df is not None:
        return render_template(
            'index.html',
            book_name=list(popular_df['Book-Title'].values),
            author=list(popular_df['Book-Author'].values),
            image=list(popular_df['Image-URL-M'].values),
            votes=list(popular_df['num_ratings'].values),
            rating=list(popular_df['avg_rating'].values)
        )
    else:
        return "Error: Data not available", 500

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    
    if user_input is None or user_input.strip() == "":
        return "Error: No book title provided", 400

    if pt is not None and similarity_scores is not None and books is not None:
        if user_input not in pt.index:
            return "Error: Book title not found in the database", 404

        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(
            list(enumerate(similarity_scores[index])),
            key=lambda x: x[1],
            reverse=True
        )[1:5]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

            data.append(item)

        print(data)

        return render_template('recommend.html', data=data)
    else:
        return "Error: Data not available", 500

if __name__ == '__main__':
    app.run(debug=True)
