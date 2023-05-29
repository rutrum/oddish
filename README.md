# Oddish

Every gen 1 pokemon as an oddish varient.

## Project ideas:

* Script that determines the color pallets used in each pokemon's image.  Theres a theme of certain colors in some number of shades.  Can I identify all of these shades from a given image?  This can be used to automatically map colors to another pallete.
    * Just map all the colors to HSV and use kmeans on hue
    * except that hue is modular so I need to write my own kmeans implementation (not that hard but annoying)
    * no! that's very wierdly defined!  Lets do this instead: Turn 1dim into a unit circle, average those
* A template/config file that defines how to transform an original pokemon sprite into oddish, with a script to read it and perform the image transformations.  It might allow the following
  * Name of the new oddish-pokemon
  * Map for how to transform one list of colors to the other
  * Location of where to draw an oddish face
  * Pixels/locations that should be erased (drawn in another color) to remove the face.  This might need to be done manually. (create and save a mask?)

## Pallete Determination

I first just tried PCA and wanted to use clustering.  But the points were too scattered, not really in clusters.  After some thought, I realized that I was concerned about groups of similar colors, ordered by lightness.  This isn't obvious in a color's representation in RGB space.  After translating to HSV space, and then reducing the points down to just their hue, I could perform clustering.  This encountered another issue however with red colors, since similar shades of red have hues near 0 and near 1.  The solution was to map the hue to the unit circle in the plane, and then perform K-means clustering.  This allows hues of value 0 and 1 to be next to one another and doesn't compromise the isolation of clusters.  This result nearly worked.

The issue is that the clusters weren't as expected.  A good example of this is Charizard, where the blues of its wings were in one group and every other color, the orange of the skin, the pale of its underside, the orange from the fire of his tail, and the white of his eyes were all grouped together.  This is when I realized I need to cluster not just based on hue, but also proximity within the image.  I have yet to use locational data in this model.  I am going to outline my next attempt at determine palletes.

First, identify frequency one color of pixel is to another.  I can construct a matrix where the i,j position of the matrix is the number of times a pixel with color i is adjacent to a pixel with color j.  This captures some sense of similarity of one color to another, maybe.  It is likely that two different colors (again, look at charizard) will be weighted highly even through they are distinct in the graph.  Perhaps some comparison of contrast should be used.  And the adjacency matrix should be scaled based on the difference in hue of the colors.  This will punish colors of different hues next to one another but not those with similar hues.

Another issue is colors with no color at all.  Grayscale colors have undefined hue, but in practice they are given a hue of 0, or red.  This also leads to charizard problem, where white is grouped with red dispite having 0 saturation.  A first pass on the colors should be taken to extract colors with least saturation.  Then regular clustering can begin on colors with defined hue, and the grayscale values will easily be given their own group.

Ordering of the values is also important.  After clustering I've just been ordering the groups based on saturation.  What I ought to do is use PCA to map the values down to 1 dimension, then order that way.  What values should I perform PCA on?  HSV or RGB? Maybe another color space?  Since my goal is optimize for value, I think its important towork in a space that uses value as a dimension, so I'll use PCA on HSV.  Since I will be clustering by hue, and colors with least saturation are removed, it is likely that the only dimension with high variabiltiy is value, so PCA will work as expected for ordering based on value, but keep slight variation in hue and saturation in mind.

Great care should be taken in the terminology used here, which I have not.  Value is not lightness, and saturation is not chroma.

### Steps, high level

1) Find data structure that weight proximity of one pixel color to another, while also incorporating hue by penalizing adjacency if hues differ substantially.
2) Manually extract low saturation values (grayscale) into their own group.
3) Use a graph-clustering method to isolate colors.
4) Order the colors of clusters based on 1-dimensional PCA of their HSV representation.

### Other random ideas / notes

* I could use a naive clustering method the seed the next attempt.  What if I could use the bad clustering results to influence the next ones? Probably not.
* What am I really measuring in this adjacent matrix?  I want to measure _proximity_.  Just because something shared a border with something else doesn't totally represent proximity.  Maybe I don't want to measure proximity but instead _continuity_.  I don't either is quite right.  I need to really think about an objective way to see, from the image, why I would want to put two colors in the same cluster, and reward values based on that.
* Magnetite sort of breaks all the rules by having red/blue as random additional colors.  Which in the case of oddish recoloring, this actually makes sense to isolate because it is unlikely values would be remapped here.
