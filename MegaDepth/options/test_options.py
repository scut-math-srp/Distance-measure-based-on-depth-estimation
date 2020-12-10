from .base_options import BaseOptions

class TestOptions(BaseOptions):
    def initialize(self):
        BaseOptions.initialize(self)
        self.parser.add_argument('--ntest', type=int, default=float("inf"), help='# of test examples.')
        self.parser.add_argument('--results_dir', type=str, default='./results/', help='saves results here.')
        self.parser.add_argument('--aspect_ratio', type=float, default=1.0, help='aspect ratio of result images')
        self.parser.add_argument('--phase', type=str, default='test', help='train, val, test, etc')
        self.parser.add_argument('--which_epoch', type=str, default='latest', help='which epoch to load? '
                                                'set to latest to use latest cached model')  # 加载哪个纪元？设置为“最新”以使用最新的缓存模型
        self.parser.add_argument('--how_many', type=int, default=50, help='how many test images to run')   # 要运行多少个测试映像
        self.isTrain = False
