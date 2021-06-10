# This file contains workload data for DNN inference use cases 
# 
# We include accesses to on-chip memory (reads, writes) storing ResNet26 and ResNet50 weights for single-task image 
# classification using the ImageNet dataset vs. multi-task image processing, comprising object detection, 
# tracking, and classification. Data is included for the case of continuous operation and intermittent operation (int).
# A consistent frame rate of 60 frames-per-second is used which is typical for HD video.
#
# We also include data for the task of natural language processing using the ALBERT network, 
# a relatively small-footprint, high-accuracy,transformer-based DNN for a range of NLP tasks. 
# We include access data for multiple cases, including embeddings only (emb), all weights (all), and
# multi-task which includes sentiment analysis and sentence similarity.

# References:
# 
# Z. Lan, M. Chen, S. Goodman, K. Gimpel, P. Sharma, and R. Soricut, “Albert: 
# A lite bert for self-supervised learning of languagerepresentations,”ArXiv, 
# vol. abs/1909.11942, 2020.

DNN_weights = {
  "names": ["ResNet50w",
            "ResNet50w_int",
            "ResNet26w_single",
            "ResNet26w_single_int",
            "ResNet26w_multi",
            "ResNet26w_multi_int",
            "ALBERTw_emb",
            "ALBERTw_all",
            "ALBERTw_multi"
  ],
  "reads": [4.7e6, #per input
            4.7e6,
            1.95e6,
            1.95e6,
            5.9e6,
            5.9e6,
            3.84e6,
            1.17e7,
            2.92e7,
  ],
  "writes": [0, #per input
             0,
             0,
             0,
             0,
             0,
             0,
             0,
             0,
  ],
  "ips": [45, #inferences per second
          1,
          45,
          1,
          45,
          1,
          1,
          1,
          1,
  ]
}

DNN_weights_acts = {
  "names": ["ResNet50",
            "ResNet50_int",
            "ResNet26_single",
            "ResNet26_single_int",
            "ResNet26_multi",
            "ResNet26_multi_int",
  ],
  "reads": [7.2e6, #per input
            7.2e6,
            2.2e6,
            2.2e6,
            6.6e6,
            6.6e6,
  ],
  "writes": [2.4e6, #per input
             2.4e6,
             0.22e6,
             0.22e6,
             0.9e6,
             0.9e6,
  ],
  "ips": [45, #inferences per second
          1,
          45,
          1,
          45,
          1,
  ]

}

