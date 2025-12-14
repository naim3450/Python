# pip install pytube
from pytube import YouTube
from pytube.exceptions import RegexMatchError

def download_video(url, save_path='.'):
    try:
        # Create YouTube object using the URL
        yt = YouTube(url)
        
        # Get the highest resolution stream available
        stream = yt.streams.get_highest_resolution()
        
        # Download the video to the specified path
        print(f"Downloading {yt.title}...")
        stream.download(output_path=save_path)
        
        print(f"Downloaded {yt.title} successfully!")
    
    except RegexMatchError:
        print("Error: Invalid YouTube URL format.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Input URL of the YouTube video
    video_url = input("Enter the YouTube video URL: ")
    
    # Optional: Specify a directory to save the video
    save_directory = input("Enter directory to save the video (or press Enter to save in current directory): ")
    
    # Download video
    download_video(video_url, save_directory if save_directory else '.')

