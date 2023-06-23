import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_imdb_movies(year, rating, genre, num_movies):
    # List to store the scraped movies
    movies = []

    # Construct the URL with the provided parameters
    url = f"https://www.imdb.com/search/title/?year={year}&title_type=feature&user_rating={rating}-&genres={genre}"

    # Send requests until the desired number of movies is reached or no more pages are available
    while len(movies) < num_movies:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the response was successful (status code 200)
        if response.status_code == 200:
            # Create a BeautifulSoup object to parse the HTML content
            soup = BeautifulSoup(response.content, "html.parser")

            # Find all the movie elements in the HTML
            movie_elements = soup.find_all("div", class_="lister-item-content")

            # Check if no movies were found
            if len(movie_elements) == 0:
                print(f"No movies found for year {year} and genre {genre}.")
                break

            # Iterate over each movie element
            for element in movie_elements:
                # Check if we have scraped the desired number of movies
                if len(movies) == num_movies:
                    break

                # Extract the title of the movie
                title_element = element.find("h3", class_="lister-item-header").find("a")
                title = title_element.text.strip()

                # Extract the year of the movie
                year = title_element.find_next_sibling("span").text.strip("()")

                # Extract the rating of the movie
                rating_element = element.find("div", class_="ratings-imdb-rating")
                if rating_element:
                    rating = rating_element.strong.text.strip()
                else:
                    rating = "N/A"  # Set a default or placeholder value if rating is not found

                # Extract the genres of the movie
                genres = [genre.strip() for genre in element.find("span", class_="genre").text.strip().split(",")]

                # Check if the provided genre is in the genres list
                if genre in genres:
                    # Set the genre to the provided genre only
                    genres = genre

                # Add the movie to the list
                movies.append({"Title": title, "Year": year, "Rating": rating, "Genres": genres})

            # Find the next page link
            next_link = soup.find("a", class_="lister-page-next")

            # Check if there is a next page
            if next_link:
                # Extract the relative URL of the next page
                next_url = next_link["href"]

                # Construct the absolute URL for the next page
                url = f"https://www.imdb.com{next_url}"
            else:
                # No more pages, exit the loop
                break

    # Check if no movies were found
    if len(movies) == 0:
        return None

    # Check if the desired number of movies exceeds the available movies
    if len(movies) < num_movies:
        print(f"Only {len(movies)} movies found for year {year} and genre {genre}.")
        return movies

    # Return the list of movies, limiting to the desired number
    return movies


def write_to_csv(movies, year):
    # Create a DataFrame from the movies list
    df = pd.DataFrame(movies)

    # Create the file name based on the year
    file_name = f"Scraped Data/imdb_top_movies_{year}.csv"

    # Write the DataFrame to a CSV file
    df.to_csv(file_name, index=False)


while True:
    try:
        year = int(input("Enter the year: "))
        rating = float(input("Enter the minimum rating: "))
        genre = input("Enter the genre: ")
        num_movies = int(input("Enter the number of movies to scrape: "))

        # Scrape the movies from IMDB
        movies = scrape_imdb_movies(year, rating, genre, num_movies)

        # Print the number of movies scraped
        if movies is not None:
            print(f"Scraped {len(movies)} movies")
            # Write the movies to a CSV file for the particular year
            write_to_csv(movies, year)
        else:
            print("No movies found. Please check your input parameters.")

        # Ask the user if they want to continue
        choice = input("Enter 1 to exit or any other key to continue: ")
        if choice == '1':
            break  # Exit the loop if the user enters 1
    except ValueError:
        print("Invalid input. Please enter valid numeric values for year, rating, and number of movies.")
