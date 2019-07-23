import argparse
import os

import tensorflow as tf
from tensorflow.contrib.learn import RunConfig

from datasets.DatasetFactory import DatasetFactory
from helper.model_helper import get_model_function, get_input_function
from nets import nets_factory

CUDA_VISIBLE_DEVICES=0
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.7
session = tf.Session(config=config)

slim = tf.contrib.slim


def start_training(data_directory, dataset_name, output_directory, network_name, batch_size, learning_rate, batch_threads, num_epochs, initial_checkpoint, checkpoint_exclude_scopes,ignore_missing_variables, trainable_scopes, not_trainable_scopes, fixed_learning_rate, learning_rate_decay_rate, do_evaluation, learning_rate_decay_steps):
    dataset_factory = DatasetFactory(dataset_name=dataset_name, data_directory=data_directory)
   
    model_params = {'learning_rate': learning_rate,'fixed_learning_rate': fixed_learning_rate,'learning_rate_decay_rate': learning_rate_decay_rate,'learning_rate_decay_steps': (dataset_factory.get_dataset('train').get_number_of_samples() if learning_rate_decay_steps is None else learning_rate_decay_steps) // batch_size}

    run_config = RunConfig(keep_checkpoint_max=10, save_checkpoints_steps=None)
    # Instantiate Estimator
    estimator = tf.estimator.Estimator(model_fn=get_model_function(output_directory, network_name, dataset_factory.get_dataset('train').num_classes(), initial_checkpoint, checkpoint_exclude_scopes, ignore_missing_variables,trainable_scopes, not_trainable_scopes,dataset_name=dataset_name),params=model_params,model_dir=output_directory,config=run_config)
    image_size = nets_factory.get_input_size(network_name)

    dataset = dataset_factory.get_dataset('train')
    #evaluation_summary_writer = get_evaluation_summary_writer(do_evaluation, output_directory)

    for epoch in range(num_epochs):
        run_training(dataset=dataset, batch_size=batch_size, batch_threads=batch_threads, epoch=epoch, estimator=estimator, num_epochs=num_epochs, image_size=image_size)
      
    print('Finished training')


def run_training(dataset, batch_size, batch_threads, epoch, estimator, num_epochs, image_size):
    print('\n\nRunning training of epoch %d of %d:\n' % (epoch + 1, num_epochs))
    train_input_function = get_input_function(dataset, batch_size, batch_threads, True, image_size)
    estimator.train(input_fn=train_input_function)
    print("-----------------------------------------")
    print('\nFinished Training epoch %d' % (epoch + 1))


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--output', help='Directory to write the output', dest='output_directory')
	parser.add_argument('--data', help='Specify the folder with the images to be trained and evaluated', dest='data_directory')
	parser.add_argument('--dataset-name', help='The name of the dataset')
	parser.add_argument('--batch-size', help='The batch size', type=int, default=16)
	parser.add_argument('--learning-rate', help='The learning rate', type=float, default=0.0001)
	parser.add_argument('--batch-threads', help='The number of threads to be used for batching', type=int, default=8)
	parser.add_argument('--num-epochs', help='The number of epochs to be trained', type=int, default=50)
	parser.add_argument('--initial-checkpoint', help='The initial model to be loaded')
	parser.add_argument('--checkpoint-exclude-scopes', help='Scopes to be excluded when loading initial checkpoint')
	parser.add_argument('--trainable-scopes', help='Scopes which will be trained')
	parser.add_argument('--not-trainable-scopes', help='Scopes which will not be trained')
	parser.add_argument('--network-name', help='Name of the network')
	parser.add_argument('--ignore-missing-variables', help='If missing variables should be ignored', action='store_true')
	parser.add_argument('--fixed-learning-rate', help='If set, no exponential learning rate decay is used', action='store_true')
	parser.add_argument('--learning-rate-decay-rate', help='The base of the learning rate decay factor', type=float, default=0.96)
	parser.add_argument('--no-evaluation', help='Do evaluation after every epoch', action='store_true')
	parser.add_argument('--learning-rate-decay-steps', help='Steps after which the learning rate is decayed', type=int, default=None)
	args = parser.parse_args()

	print('Running with command line arguments:')
	print(args)
	print('\n\n')

	# tf.logging.set_verbosity(tf.logging.INFO)

	if not os.path.exists(args.output_directory):
		os.makedirs(args.output_directory)

	start_training(args.data_directory, args.dataset_name, args.output_directory, args.network_name, args.batch_size, args.learning_rate, args.batch_threads, args.num_epochs,
				   args.initial_checkpoint, args.checkpoint_exclude_scopes, args.ignore_missing_variables, args.trainable_scopes, args.not_trainable_scopes, args.fixed_learning_rate,
				   args.learning_rate_decay_rate, not args.no_evaluation, args.learning_rate_decay_steps)

	print('Exiting ...')


if __name__ == '__main__':
	main()
