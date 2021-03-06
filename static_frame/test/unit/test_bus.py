import unittest
# from io import StringIO
import numpy as np

from static_frame.core.frame import Frame
from static_frame.core.bus import Bus
from static_frame.core.bus import FrameDeferred

from static_frame.core.series import Series

from static_frame.core.store_zip import StoreZipTSV

from static_frame.core.store import StoreConfigMap
from static_frame.core.store import StoreConfig
from static_frame.core.display import DisplayConfig

from static_frame.test.test_case import TestCase
from static_frame.test.test_case import temp_file
from static_frame.test.test_case import skip_win

# from static_frame.test.test_case import skip_win
from static_frame.core.exception import ErrorInitBus
from static_frame.core.exception import StoreFileMutation


class TestUnit(TestCase):

    def test_frame_deferred_a(self) -> None:

        self.assertEqual(str(FrameDeferred), '<FrameDeferred>')

    def test_bus_slotted_a(self) -> None:

        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='foo')

        b1 = Bus.from_frames((f1,))

        with self.assertRaises(AttributeError):
            b1.g = 30 # type: ignore #pylint: disable=E0237
        with self.assertRaises(AttributeError):
            b1.__dict__ #pylint: disable=W0104

    def test_bus_init_a(self) -> None:

        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='foo')
        f2 = Frame.from_dict(
                dict(a=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='bar')

        config = StoreConfigMap.from_config(StoreConfig(index_depth=1))
        b1 = Bus.from_frames((f1, f2), config=config)

        self.assertEqual(b1.keys().values.tolist(),
                ['foo', 'bar'])


        with temp_file('.zip') as fp:
            b1.to_zip_tsv(fp)
            b2 = Bus.from_zip_tsv(fp)

            f3 = b2['bar']
            f4 = b2['foo']
            # import ipdb; ipdb.set_trace()
            zs = StoreZipTSV(fp)
            zs.write(b1.items())

            # how to show that this derived getitem has derived type?
            f3 = zs.read('foo', config=config['foo'])
            self.assertEqual(
                f3.to_pairs(0),
                (('a', (('x', 1), ('y', 2))), ('b', (('x', 3), ('y', 4))))
            )

    def test_bus_init_b(self) -> None:

        with self.assertRaises(ErrorInitBus):
            Bus(Series([1, 2, 3]))

        with self.assertRaises(ErrorInitBus):
            Bus(Series([3, 4], dtype=object))

        with self.assertRaises(ErrorInitBus):
            Bus(Series([3, 4], index=('a', 'b'), dtype=object))


    def test_bus_init_c(self) -> None:

        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='foo')
        f2 = Frame.from_dict(
                dict(a=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='bar')

        config = StoreConfigMap.from_config(StoreConfig(index_depth=1))
        b1 = Bus.from_frames((f1, f2), config=config)

        self.assertEqual(b1.keys().values.tolist(),
                ['foo', 'bar'])

        with temp_file('.zip') as fp:
            b1.to_zip_csv(fp)
            b2 = Bus.from_zip_csv(fp, config=config)

            f1_loaded = b2['foo']
            f2_loaded = b2['bar']

            self.assertEqualFrames(f1, f1_loaded)
            self.assertEqualFrames(f2, f2_loaded)

    def test_bus_shapes_a(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f2 = Frame.from_dict(
                dict(a=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f3 = Frame.from_dict(
                dict(a=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')

        b1 = Bus.from_frames((f1, f2, f3))

        with temp_file('.zip') as fp:

            b1.to_zip_pickle(fp)

            b2 = Bus.from_zip_pickle(fp)

            f2_loaded = b2['f2']

            self.assertEqual(b2.shapes.to_pairs(),
                    (('f1', None), ('f2', (3, 2)), ('f3', None)))

            f3_loaded = b2['f3']

            self.assertEqual(b2.shapes.to_pairs(),
                    (('f1', None), ('f2', (3, 2)), ('f3', (2, 2 )))
                    )

    @skip_win # type: ignore
    def test_bus_nbytes_a(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f2 = Frame.from_dict(
                dict(a=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f3 = Frame.from_dict(
                dict(a=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')

        b1 = Bus.from_frames((f1, f2, f3))

        with temp_file('.zip') as fp:
            b1.to_zip_pickle(fp)
            b2 = Bus.from_zip_pickle(fp)

            f2_loaded = b2['f2']

            self.assertEqual(b2.nbytes, 48)

            f3_loaded = b2['f3']

            self.assertEqual(b2.nbytes, 80)

            f1_loaded = b2['f1']

            self.assertEqual(b2.nbytes, 112)


    @skip_win # type: ignore
    def test_bus_dtypes_a(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f2 = Frame.from_dict(
                dict(c=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f3 = Frame.from_dict(
                dict(d=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')

        b1 = Bus.from_frames((f1, f2, f3))

        with temp_file('.zip') as fp:
            b1.to_zip_pickle(fp)
            b2 = Bus.from_zip_pickle(fp)

            self.assertEqual(b2.dtypes.to_pairs(0), ())

            f2_loaded = b2['f2']

            self.assertEqual(b2.dtypes.to_pairs(0),
                    (('c', (('f1', None), ('f2', np.dtype('int64')), ('f3', None))), ('b', (('f1', None), ('f2', np.dtype('int64')), ('f3', None))))
            )

            f3_loaded = b2['f3']

            self.assertEqual(b2.dtypes.to_pairs(0),
                    (('b', (('f1', None), ('f2', np.dtype('int64')), ('f3', np.dtype('int64')))), ('c', (('f1', None), ('f2', np.dtype('int64')), ('f3', None))), ('d', (('f1', None), ('f2', None), ('f3', np.dtype('int64')))))
                    )


    def test_bus_mloc_a(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f2 = Frame.from_dict(
                dict(c=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f3 = Frame.from_dict(
                dict(d=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')

        b1 = Bus.from_frames((f1, f2, f3))

        with temp_file('.zip') as fp:
            b1.to_zip_pickle(fp)
            b2 = Bus.from_zip_pickle(fp)

            f2_loaded = b2['f2']

            mloc1 = b2.mloc

            f3_loaded = b2['f3']
            f1_loaded = b2['f1']

            self.assertEqual(mloc1['f2'], b2.mloc.loc['f2'])


    @skip_win # type: ignore
    def test_bus_status_a(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f2 = Frame.from_dict(
                dict(c=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f3 = Frame.from_dict(
                dict(d=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')

        b1 = Bus.from_frames((f1, f2, f3))

        with temp_file('.zip') as fp:
            b1.to_zip_pickle(fp)
            b2 = Bus.from_zip_pickle(fp)

            status = b2.status
            self.assertEqual(status.shape, (3, 4))
            # force load all
            tuple(b2.items())

            self.assertEqual(
                    b2.status.to_pairs(0),                                                           (('loaded', (('f1', True), ('f2', True), ('f3', True))), ('size', (('f1', 4.0), ('f2', 6.0), ('f3', 4.0))), ('nbytes', (('f1', 32.0), ('f2', 48.0), ('f3', 32.0))),('shape', (('f1', (2, 2)), ('f2', (3, 2)), ('f3', (2, 2)))))
            )


    def test_bus_keys_a(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f2 = Frame.from_dict(
                dict(c=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f3 = Frame.from_dict(
                dict(d=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')
        f4 = Frame.from_dict(
                dict(q=(None,None), r=(np.nan,np.nan)),
                index=(1000, 1001),
                name='f4')

        b1 = Bus.from_frames((f1, f2, f3, f4))

        self.assertEqual(b1.keys().values.tolist(), ['f1', 'f2', 'f3', 'f4'])
        self.assertEqual(b1.values[2].name, 'f3')

        with temp_file('.zip') as fp:
            b1.to_zip_pickle(fp)
            b2 = Bus.from_zip_pickle(fp)
            self.assertFalse(b2._loaded_all)

            self.assertEqual(b2.keys().values.tolist(), ['f1', 'f2', 'f3', 'f4'])
            self.assertFalse(b2._loaded.any())
            # accessing values forces loading all
            self.assertEqual(b2.values[2].name, 'f3')
            self.assertTrue(b2._loaded_all)


    def test_bus_reversed_a(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f2 = Frame.from_dict(
                dict(c=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f3 = Frame.from_dict(
                dict(d=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')

        b1 = Bus.from_frames((f1, f2, f3))
        self.assertEqual(list(reversed(b1)), ['f3', 'f2', 'f1'])


    def test_bus_display_a(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f2 = Frame.from_dict(
                dict(c=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f3 = Frame.from_dict(
                dict(d=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')

        b1 = Bus.from_frames((f1, f2, f3))
        self.assertEqual(
                b1.display(config=DisplayConfig(type_color=False)).to_rows(),
                ['<Bus>',
                '<Index>',
                'f1      Frame',
                'f2      Frame',
                'f3      Frame',
                '<<U2>   <object>'])

        rows1 = b1.display(config=DisplayConfig(
                type_color=False,
                type_show=False)).to_rows()
        self.assertEqual(rows1, ['f1 Frame', 'f2 Frame', 'f3 Frame'])

        rows2 = b1.display(config=DisplayConfig(
                type_color=False,
                type_show=False,
                include_index=False)).to_rows()
        self.assertEqual(rows2, ['Frame', 'Frame', 'Frame'])



    #---------------------------------------------------------------------------
    def test_bus_iloc_a(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f2 = Frame.from_dict(
                dict(c=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f3 = Frame.from_dict(
                dict(d=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')

        b1 = Bus.from_frames((f1, f2, f3))

        with temp_file('.zip') as fp:
            b1.to_zip_pickle(fp)
            b2 = Bus.from_zip_pickle(fp)

            self.assertEqual(
                    b2.iloc[[0, 2]].status['loaded'].to_pairs(),
                    (('f1', True), ('f3', True))
                    )

    def test_bus_iloc_b(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')

        b1 = Bus.from_frames((f1,))
        f2 = b1.iloc[0]
        self.assertTrue(f1 is f2)

    def test_bus_loc_a(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')

        b1 = Bus.from_frames((f1,))
        f2 = b1.loc['f1']
        self.assertTrue(f1 is f2)

    def test_bus_loc_b(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f2 = Frame.from_dict(
                dict(c=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f3 = Frame.from_dict(
                dict(d=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')

        b1 = Bus.from_frames((f1, f2, f3))
        b2 = b1.loc['f2':] #type: ignore
        self.assertEqual(len(b2), 2)
        self.assertEqual(b2.index.values.tolist(), ['f2', 'f3'])


    def test_bus_getitem_a(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f2 = Frame.from_dict(
                dict(c=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f3 = Frame.from_dict(
                dict(d=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')

        b1 = Bus.from_frames((f1, f2, f3))

        with temp_file('.zip') as fp:
            b1.to_zip_pickle(fp)
            b2 = Bus.from_zip_pickle(fp)

            self.assertEqual(b2['f2':].status['loaded'].to_pairs(), #type: ignore
                    (('f2', True), ('f3', True))
                    )


    def test_bus_to_xlsx_a(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f2 = Frame.from_dict(
                dict(c=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f3 = Frame.from_dict(
                dict(d=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')

        config = StoreConfigMap.from_config(
                StoreConfig(
                        index_depth=1,
                        columns_depth=1,
                        include_columns=True,
                        include_index=True
                        ))
        b1 = Bus.from_frames((f1, f2, f3), config=config)

        with temp_file('.xlsx') as fp:
            b1.to_xlsx(fp)

            b2 = Bus.from_xlsx(fp, config=config)
            tuple(b2.items()) # force loading all

        for frame in (f1, f2, f3):
            self.assertEqualFrames(frame, b2[frame.name])


    def test_bus_to_xlsx_b(self) -> None:

        f1 = Frame.from_dict(
                dict(a=(1,2,3)),
                index=('x', 'y', 'z'),
                name='f1')
        f2 = Frame.from_dict(
                dict(A=(10,20,30)),
                index=('q', 'r', 's'),
                name='f2')

        config = StoreConfig(include_index=True, index_depth=1)
        b1 = Bus.from_frames((f1, f2), config=config)

        with temp_file('.xlsx') as fp:
            b1.to_xlsx(fp)

            b2 = Bus.from_xlsx(fp, config=config)
            tuple(b2.items()) # force loading all

        for frame in (f1, f2):
            self.assertEqualFrames(frame, b2[frame.name])



    def test_bus_to_xlsx_c(self) -> None:
        '''
        Test manipulating a file behind the Bus.
        '''
        f1 = Frame.from_dict(
                dict(a=(1,2,3)),
                index=('x', 'y', 'z'),
                name='f1')

        f2 = Frame.from_dict(
                dict(x=(10,20,30)),
                index=('q', 'r', 's'),
                name='f2')

        b1 = Bus.from_frames((f1,),)

        with temp_file('.xlsx') as fp:

            b1.to_xlsx(fp)

            b2 = Bus.from_xlsx(fp)

            f2.to_xlsx(fp)

            with self.assertRaises(StoreFileMutation):
                tuple(b2.items())


    def test_bus_to_xlsx_d(self) -> None:
        '''
        Test manipulating a file behind the Bus.
        '''
        f1 = Frame.from_dict(
                dict(a=(1,2,3)),
                index=('x', 'y', 'z'),
                name='f1')

        b1 = Bus.from_frames((f1,),)

        with temp_file('.xlsx') as fp:

            b1.to_xlsx(fp)

            b2 = Bus.from_xlsx(fp)

        with self.assertRaises(StoreFileMutation):
            tuple(b2.items())


    #---------------------------------------------------------------------------
    def test_bus_to_sqlite_a(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f2 = Frame.from_dict(
                dict(c=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f3 = Frame.from_dict(
                dict(d=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')

        frames = (f1, f2, f3)
        config = StoreConfigMap.from_frames(frames)
        b1 = Bus.from_frames(frames, config=config)

        with temp_file('.sqlite') as fp:
            b1.to_sqlite(fp)
            b2 = Bus.from_sqlite(fp, config=config)
            tuple(b2.items()) # force loading all

        for frame in frames:
            self.assertEqualFrames(frame, b2[frame.name])


    def test_bus_to_sqlite_b(self) -> None:
        '''
        Test manipulating a file behind the Bus.
        '''
        f1 = Frame.from_dict(
                dict(a=(1,2,3)),
                index=('x', 'y', 'z'),
                name='f1')

        b1 = Bus.from_frames((f1,),)

        with temp_file('.db') as fp:

            b1.to_sqlite(fp)

            b2 = Bus.from_sqlite(fp)

        with self.assertRaises(StoreFileMutation):
            tuple(b2.items())

    def test_bus_to_hdf5_a(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f2 = Frame.from_dict(
                dict(c=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f3 = Frame.from_dict(
                dict(d=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')

        frames = (f1, f2, f3)
        config = StoreConfigMap.from_frames(frames)
        b1 = Bus.from_frames(frames, config=config)

        with temp_file('.h5') as fp:
            b1.to_hdf5(fp)
            b2 = Bus.from_hdf5(fp, config=config)
            tuple(b2.items()) # force loading all

        for frame in frames:
            self.assertEqualFrames(frame, b2[frame.name])


    def test_bus_to_hdf5_b(self) -> None:
        '''
        Test manipulating a file behind the Bus.
        '''
        f1 = Frame.from_dict(
                dict(a=(1,2,3)),
                index=('x', 'y', 'z'),
                name='f1')

        b1 = Bus.from_frames((f1,),)

        with temp_file('.h5') as fp:

            b1.to_hdf5(fp)

            b2 = Bus.from_hdf5(fp)

        with self.assertRaises(StoreFileMutation):
            tuple(b2.items())

    #---------------------------------------------------------------------------


    def test_bus_equals_a(self) -> None:

        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f2 = Frame.from_dict(
                dict(c=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f3 = Frame.from_dict(
                dict(d=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')

        f4 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='f1')
        f5 = Frame.from_dict(
                dict(c=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='f2')
        f6 = Frame.from_dict(
                dict(d=(10,20), b=(50,60)),
                index=('p', 'q'),
                name='f3')

        f7 = Frame.from_dict(
                dict(d=(10,20), b=(50,61)),
                index=('p', 'q'),
                name='f3')


        b1 = Bus.from_frames((f1, f2, f3))
        b2 = Bus.from_frames((f1, f2, f3))
        b3 = Bus.from_frames((f4, f5, f6))
        b4 = Bus.from_frames((f4, f5, f7))
        b5 = Bus.from_frames((f4, f5))
        b6 = Bus.from_frames((f3, f2, f1))

        self.assertTrue(b1.equals(b2))
        self.assertTrue(b1.equals(b3))

        self.assertFalse(b1.equals(b4))
        self.assertFalse(b1.equals(b5))
        self.assertFalse(b1.equals(b6))

    #---------------------------------------------------------------------------


    def test_bus_interface_b(self) -> None:
        f1 = Frame.from_dict(
                dict(a=(1,2), b=(3,4)),
                index=('x', 'y'),
                name='foo')
        f2 = Frame.from_dict(
                dict(a=(1,2,3), b=(4,5,6)),
                index=('x', 'y', 'z'),
                name='bar')

        b1 = Bus.from_frames((f1, f2))
        post1 = b1.interface
        self.assertTrue(isinstance(post1, Frame))
        self.assertTrue(post1.shape, (41, 3))

        post2 = Bus.interface
        self.assertTrue(isinstance(post2, Frame))
        self.assertTrue(post2.shape, (41, 3)) #type: ignore


    #---------------------------------------------------------------------------

    def test_bus_mlox_a(self) -> None:

        f1 = Frame.from_dict(
                dict(a=(1,2,3)),
                index=('x', 'y', 'z'),
                name='f1')
        b1 = Bus.from_frames((f1,),)

        with temp_file('.db') as fp:

            b1.to_sqlite(fp)
            b2 = Bus.from_sqlite(fp)

            mloc = b2.mloc

            self.assertEqual(mloc.to_pairs(),
                    (('f1', None),))



if __name__ == '__main__':

    unittest.main()

