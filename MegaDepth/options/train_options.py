from .base_options import BaseOptions

class TrainOptions(BaseOptions):
    def initialize(self):
        BaseOptions.initialize(self)
        self.parser.add_argument('--display_freq', type=int, default=100, help='frequency of showing training results on screen')
        self.parser.add_argument('--print_freq', type=int, default=100, help='frequency of showing training results on console')
        self.parser.add_argument('--save_latest_freq', type=int, default=5000, help='frequency of saving the latest results')
        self.parser.add_argument('--save_epoch_freq', type=int, default=5, help='frequency of saving checkpoints at the end of epochs')
        self.parser.add_argument('--continue_train', action='store_true', help='continue training: load the latest model')
        self.parser.add_argument('--phase', type=str, default='train', help='train, val, test, etc')
        self.parser.add_argument('--which_epoch', type=str, default='latest', help='which epoch to load? set to latest to use latest cached model')
        self.parser.add_argument('--niter', type=int, default=100, help='# of iter at starting learning rate')     # 开始学习速率
        self.parser.add_argument('--niter_decay', type=int, default=100, help='# of iter to linearly decay learning rate to zero')  # 线性衰减到零学习率
        self.parser.add_argument('--beta1', type=float, default=0.5, help='momentum term of adam')                     # 亚当动量项
        self.parser.add_argument('--lr', type=float, default=0.0002, help='initial learning rate for adam')            # adam的初始学习率
        self.parser.add_argument('--no_lsgan', action='store_true', help='do *not* use least square GAN, if false, use vanilla GAN')   # 不要用最小二乘法，如果是假的，用香草根
        self.parser.add_argument('--lambda_A', type=float, default=10.0, help='weight for cycle loss (A -> B -> A)')   # 循环损耗重量（A->B->A）
        self.parser.add_argument('--lambda_B', type=float, default=10.0, help='weight for cycle loss (B -> A -> B)')   # 循环损耗重量（B->A->B）
        self.parser.add_argument('--pool_size', type=int, default=50, help='the size of image buffer that stores previously generated images')  # 存储先前生成的图像的图像缓冲区的大小
        self.parser.add_argument('--no_html', action='store_true', help='do not save intermediate training results to [opt.checkpoints_dir]/[opt.name]/web/')   # 不要将中间培训结果保存到[可选检查点\u dir]/[选择名称]/网络/
        self.parser.add_argument('--no_flip'  , action='store_true', help='if specified, do not flip the images for data argumentation')             # 如果指定，请勿翻转图像以进行数据论证

        # NOT-IMPLEMENTED self.parser.add_argument('--preprocessing', type=str, default='resize_and_crop', help='resizing/cropping strategy')
        self.isTrain = True
