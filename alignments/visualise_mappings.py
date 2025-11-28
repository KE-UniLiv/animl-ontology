import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os


def visualise_logmap_mappings(dataframe, output_file):
    """
    Visualise LogMap mappings using a heatmap.
    
    Parameters:
    - dataframe: Pandas DataFrame containing the mappings with columns 'source', 'target', and 'score'.
    - output_file: Path to save the heatmap image.
    """
    
    sns.scatterplot(data=dataframe, x='source', y='target', hue='score', size='score', sizes=(20, 200), alpha=0.6)
    
    # Create a heatmap
    #sns.heatmap(pivot_table, annot=True, fmt=".2f", cmap="YlGnBu")
    
    plt.show()

    # Save the heatmap to a file
    plt.savefig(output_file)
    plt.close()

if __name__ == "__main__":

    path = os.path.join(os.getcwd(), "alignment", "outputs", "logmap2_mappings.owllogmap_anchors.tsv")
    # Example usage
    df = pd.read_csv(path, sep="\t", header=None, names=["source", "target", "score"])
    visualise_logmap_mappings(df, "logmap_heatmap.png")
    print("Heatmap saved as logmap_heatmap.png")