#!/usr/bin/env python3

# Importing the required modules for this program
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from config import device


############################################################################
######     Specify transform(s) to be applied to the input images     ######
############################################################################
def transform(mode):
    """
    This method is called during loading of the data and it applies transformation to the training and test data.
    I applied several transformations to testing data to enhance the training data set and reduce overfitting but 
    only applied normalize to test data as wanted to test the original image and not any augmented image.    
    """
    if mode == 'train':
        transform=transforms.Compose([
            transforms.RandomHorizontalFlip(0.6),                           # flips the image horizontally with a probability of 0.6
            transforms.RandomRotation(degrees=[-90, 90]),                   # randomly rotates images from degrees -90 to +90
            transforms.RandomPerspective(distortion_scale=0.4, p=0.2),      # changes the image perspective with distortion value 0.4 and probability 0.2
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))                            # normalize the training data with mean 0.5 and standard deviation 0.5
            ])
        return transform
    elif mode == 'test':
        transform=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))                            # normalize the test data with mean 0.5 and standard deviation 0.5
            ])
        return transform


############################################################################
######   Define the Module to process the images and produce labels   ######
############################################################################
class Network(nn.Module):
    
    """
    I have used a VGG architecture for this model and updated it as per the requirements.
    It has 3 convolutional blocks followed by 2 fully connected layers and the output layer.
    All the 3 convolutional blocks have 2 convolutional layers followed by a batch norm layer.
    First two convolutional blocks also have max pooling while the third block doesn't.
    All the six convolutional layers (of 3 blocks) have a kernel size of 3.
    All the conv and FC layers have RELU as an activation function and final layer has log_sofmax.
    Dropout is also applied to the two fully connected layers.
    This network takes four parameters as its inputs:
        1st param includes the number of filters in convolutional blocks 1, 2 and 3.
        2nd param includes the number of hidden parameters in fully connected layers 1 and 2.
        3rd param is the number of output classes.
        4th param is the value of droptout used in 2 fully connected layers.
    """
    def __init__(self, filters, fc_hids, output_classes, dropout = 0.0):
        super().__init__()

        # conv block 1
        self.conv1_1 = nn.Conv2d(in_channels=3, out_channels=filters[0], kernel_size=3)             # defining 1st conv layer of 1st block
        self.conv2_1 = nn.Conv2d(in_channels=filters[0], out_channels=filters[0], kernel_size=3)    # defining 2nd conv layer of 1st block
        self.conv_batch_norm_1 = nn.BatchNorm2d(filters[0])                                         # batch normalization layer
        self.conv_max_pool_1 = nn.MaxPool2d(2)                                                      # max pooling layer
        
        # conv block 2
        self.conv1_2 = nn.Conv2d(in_channels=filters[0], out_channels=filters[1], kernel_size=3)    # defining 1st conv layer of 2nd block
        self.conv2_2 = nn.Conv2d(in_channels=filters[1], out_channels=filters[1], kernel_size=3)    # defining 2nd conv layer of 2nd block
        self.conv_batch_norm_2 = nn.BatchNorm2d(filters[1])                                         # batch normalization layer
        self.conv_max_pool_2 = nn.MaxPool2d(2)                                                      # max pooling layer
        
        # conv block 3
        self.conv1_3 = nn.Conv2d(in_channels=filters[1], out_channels=filters[2], kernel_size=3)    # defining 1st conv layer of 3rd block
        self.conv2_3 = nn.Conv2d(in_channels=filters[2], out_channels=filters[2], kernel_size=3)    # defining 2nd conv layer of 3rd block
        self.conv_batch_norm_3 = nn.BatchNorm2d(filters[2])                                         # batch normalization layer
        
        # fc block 1
        self.fc_linear_1 = nn.Linear(21632, fc_hids[0])                 # 1st fully connected layer with 21632 input parameters
        self.fc_dropout_1 = nn.Dropout(p=dropout)                       # applying dropout with supplied probability on 1st FC layer

        # fc block 2
        self.fc_linear_2 = nn.Linear(fc_hids[0], fc_hids[1])            # 2nd fully connected layer
        self.fc_dropout_2 = nn.Dropout(p=dropout)                       # applying dropout with supplied probability on 2nd FC layer

        # fc final output layer
        self.output_layer = nn.Linear(fc_hids[1], output_classes)       # final output layer to classify the supplied number of output classes
        
    def forward(self, input):
        
        x = input                           # gets input image of dimension 3x80x80

        # conv block 1
        x = self.conv1_1(x)                 # image size changed to 32x78x78
        x = F.relu(x)
        x = self.conv2_1(x)                 # image size changed to 32x76x76
        x = self.conv_batch_norm_1(x)
        x = F.relu(x)
        x = self.conv_max_pool_1(x)         # image size changed to 32x38x38

        # conv block 2
        x = self.conv1_2(x)                 # image size changed to 64x36x36
        x = F.relu(x)
        x = self.conv2_2(x)                 # image size changed to 64x34x34
        x = self.conv_batch_norm_2(x)
        x = F.relu(x)
        x = self.conv_max_pool_1(x)         # image size changed to 64x17x17

        # conv block 3
        x = self.conv1_3(x)                 # image size changed to 128x15x15
        x = F.relu(x)
        x = self.conv2_3(x)                 # image size changed to 128x13x13
        x = self.conv_batch_norm_3(x)
        x = F.relu(x)

        x = x.view(x.shape[0], -1)          # flatten the image to 21632 1-d parameters

        # fc block 1
        x = self.fc_linear_1(x)             # reduced the output to 512 1-d parameters
        x = F.relu(x)
        x = self.fc_dropout_1(x)            # applied dropout to the output parameters

        # fc block 2
        x = self.fc_linear_2(x)             # reduced the output to 128 1-d parameters
        x = F.relu(x)
        x = self.fc_dropout_2(x)            # applied dropout to the output parameters
        
        x = self.output_layer(x)            # final output has size 8, corresponding to 8 cat classes

        output = F.log_softmax(x, dim=1)    # applied log softmax activation at final output layer
        return output

"""
Defining a VGG model with the required parameters.
1st array includes the filter values of 32, 64 and 128 for convolutional blocks 1, 2 and 3 respectively.
2nd array included the number of hidden parameters 512 and 128 for fully connected layers 1 and 2.
Number of output classes is 8 and dropout value selected is 0.73.
"""
net = Network([32, 64, 128], [512, 128], 8, 0.73).to(device)

    
############################################################################
######      Specify the optimizer and loss function                   ######
############################################################################

# Using Adam optimizer with a learning rate of 0.001
optimizer = optim.Adam(net.parameters(), lr=0.001)

# Using Cross Entropy (log loss) as our loss function
loss_func = torch.nn.CrossEntropyLoss()


############################################################################
######  Custom weight initialization and lr scheduling are optional   ######
############################################################################

# Below weight initialization method can be used to overcome exploding and vanishing gradients
def weights_init(m):
    """
    if type(m) == nn.Linear:
        nn.init.xavier_uniform_(m.weight)
        m.bias.data.fill_(0)
    elif type(m) == nn.Conv2d:
        nn.init.xavier_uniform_(m.weight)
        m.bias.data.fill_(0.01)
    """
    return

scheduler = None

############################################################################
#######              Metaparameters and training options              ######
############################################################################

dataset = "./data"

# During the testing, I used a 80:20 split for training and validation data
# When the testing was finished and model was finalized, I trained it on the whole data
train_val_split = 0.999  

# Using a batch size of 128 for training the data
batch_size = 128            

# Running the code till 1000 epochs to let it converge fully and find the global minima
epochs = 1000               
                            
