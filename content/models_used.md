<!-- "Models Used" page copy. Edit the words; each block starts with @name.
     The page (sections/models_used.py) decides where each block appears. -->

@intro
Three kinds of model do the work on this site. Here's what each one is, and what it does for us.

@mlp
**MLP (multilayer perceptron)** — an MLP is built from neurons: simple nodes that connect to each other, fully connected from one layer to the next. Using non-linear functions like ReLU and sigmoid, it learns complex, non-linear relationships in data, which makes it good for classification and prediction. In our project, the MLP sees six features describing four facts about a dog — its age, whether it's mixed-breed, its sex, and whether it's been spayed or neutered — and from those it learns rough rules for how likely a dog is to be adopted.

@cnn
**CNN (convolutional neural network)** — a CNN is built to read grid-like data, most notably images. Instead of connecting every pixel to every node, it slides a small filter — a kind of digital magnifying glass — across the image piece by piece. It starts by spotting simple things like edges and textures, then combines them into complex features like floppy ears, a snout, or a wagging tail. In our project we use a lightweight image scanner called ConvNeXt-Tiny: it looks at a dog's photo and turns the raw picture into meaningful visual clues about the dog.

@multitask
**Multi-task model** — a multi-task model follows a two-birds-with-one-stone idea: instead of training a model to do one job, we train it to do several related jobs at once. It shares a single backbone to read the input, then splits into separate branches at the end to give different answers. In our project, the model takes a dog's photo and demographics and answers two questions at the same time: "Will this dog get adopted?" (the main goal) and "Is this dog young or old?" (a useful side goal, since age helps predict adoption). Because the model is forced to practice guessing age, it gets better at spotting telling visual details — gray muzzles, puppy-like features — which makes its final adoption prediction more accurate.
