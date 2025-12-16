import unittest

from pydantic import ValidationError
from pyswark.lib.pydantic import ser_des
from pyswark.core.models import collection, primitive


class TestTuple(unittest.TestCase):

    def test_extract(self):
        model = collection.Tuple([ False, 1, primitive.Bool(1), 1.0, primitive.Float('1.0'), '1.0' ])
        self.assertTupleEqual( model.extract(), (False, 1, True, 1.0, 1.0, '1.0') )

    def test_serialization_roundtrip(self):
        model = collection.Tuple([ False, 1, primitive.Bool(1), 1.0, primitive.Float('1.0'), '1.0' ])
        ser = model.toJson()
        des = ser_des.fromJson( ser )
        self.assertTupleEqual( model.extract(), des.extract() )

    def test_nested_serialization_roundtrip(self):
        model = collection.Tuple(( False, ))
        model = collection.Tuple(((( model, ), model, ), model, ))
        ser = model.toJson()
        des = ser_des.fromJson( ser )
        self.assertTupleEqual( model.extract(), des.extract() )


class TestSet(unittest.TestCase):

    def test_serialization_roundtrip(self):
        model = collection.Set([ False, 1, primitive.Bool(1), 1.0, primitive.Float('1.0'), '1.0' ])
        ser = model.toJson()
        des = ser_des.fromJson( ser )
        self.assertSetEqual( model.extract(), des.extract() )


class TestList(unittest.TestCase):

    def test_nested_serialization_roundtrip(self):
        model = collection.List([ False, ])
        model = collection.List([[[ model, ], model, ], model, ])
        ser = model.toJson()
        des = ser_des.fromJson( ser )
        self.assertListEqual( model.extract(), des.extract() )


class TestListAsDict(unittest.TestCase):

    def test_with_simple_values(self):
        """Test asDict() on a simple list - should use enumeration"""
        model = collection.List([1, 2, 3])
        result = model.asDict()
        self.assertIsInstance(result, collection.Dict)
        self.assertDictEqual(result.extract(), {0: 1, 1: 2, 2: 3})

    def test_with_mixed_tuple_lengths(self):
        """Test asDict() on a list with mixed tuple lengths"""
        model = collection.List([(1, 2, 3), (4, 5)])
        result = model.asDict()
        self.assertIsInstance(result, collection.Dict)
        self.assertDictEqual(result.extract(), {1: (2, 3), 4: 5})

    def test_with_dicts(self):
        """Test asDict() with a list containing dictionaries"""
        model = collection.List([{1: 2}, {3: 4}])
        result = model.asDict()
        self.assertIsInstance(result, collection.Dict)
        self.assertDictEqual(result.extract(), {0: {1: 2}, 1: {3: 4}})

    def test_with_dicts_and_tuples(self):
        """Test asDict() with a list containing both dicts and tuples"""
        model = collection.List([{1: 2}, {2: 3}, (3, 4)])
        result = model.asDict()
        self.assertIsInstance(result, collection.Dict)
        self.assertDictEqual(result.extract(), {1: 2, 2: 3, 3: 4})

    def test_with_multi_key_dicts(self):
        """Test asDict() with dictionaries containing multiple key-value pairs"""
        model = collection.List([{1: 2, 3: 4}, (5, 6)])
        result = model.asDict()
        self.assertIsInstance(result, collection.Dict)
        self.assertDictEqual(result.extract(), {1: 2, 3: 4, 5: 6})

    def test_with_dicts_and_3tuples(self):
        """Test asDict() with dicts and 3+-tuples"""
        model = collection.List([{1: 2}, (3, 4, 5)])
        result = model.asDict()
        self.assertIsInstance(result, collection.Dict)
        self.assertDictEqual(result.extract(), {1: 2, 3: (4, 5)})

    def test_raises_on_duplicate_keys(self):
        """Test that duplicate keys raise a ValueError"""
        model = collection.List([(1, 2), (1, 4)])
        with self.assertRaises(ValueError) as context:
            model.asDict()
        self.assertIn("must be unique", str(context.exception))

    def test_with_list_of_records(self):
        """Test asDict() with a list of record-like dicts - should enumerate them"""
        records = [
            {"name": "A", "data": 1},
            {"name": "B", "data": 2},
        ]
        model = collection.List(records)
        result = model.asDict()
        self.assertIsInstance(result, collection.Dict)
        self.assertDictEqual(result.extract(), {
            0: {"name": "A", "data": 1},
            1: {"name": "B", "data": 2},
        })


class TestDict(unittest.TestCase):

    def test_extract(self):
        model = collection.Dict({ 1:2, '3': ( primitive.Bool(0), )})
        self.assertDictEqual( model.extract(), { 1:2, '3': ( False, )})

    def test_serialization_roundtrip(self):
        model = collection.Dict({ 1:2, '3': ( primitive.Bool(0), )})
        ser = model.toJson()
        des = ser_des.fromJson( ser )
        self.assertDictEqual( model.extract(), des.extract() )

    def test_extract_with_different_objects(self):
        model = collection.Dict([(1,2), [3, (4,)], {5, 6}, {7:(8,9,10,{11:12})}])
        self.assertDictEqual( model.extract(), {1:2, 3:(4,), 5:6, 7:(8,9,10,{11:12})})

    def test_handles_dict_as_value(self):
        """Test that Dict properly handles dicts as values"""
        model = collection.Dict([
            (1,2, 3),
            (10, {20, 30}),
            {2, 3, 4}, 
            [7,8,9],
        ])
        ser = model.toJson()
        des = ser_des.fromJson( ser )

        self.assertDictEqual(des.extract(), {1: (2, 3), 10: {20, 30}, 2: {3, 4}, 7: [8, 9]})


class TestDictValidation(unittest.TestCase):

    def test_rejects_duplicate_keys(self):
        with self.assertRaises(ValidationError) as context:
            collection.Dict([(1,2), (1,3)])
        self.assertIn("must be unique", str(context.exception))

    def test_rejects_invalid_length(self):
        with self.assertRaises(ValidationError) as context:
            collection.Dict([(1,)])
        self.assertIn("length of 2 or more, got 1", str(context.exception))

    def test_handles_length_greater_than_2(self):
        model = collection.Dict([(1,2,3)])
        self.assertDictEqual(model.extract(), {1: (2, 3)})

    def test_extract_raises_on_duplicate_keys(self):
        """Test that Dict directly with duplicate keys raises a ValueError"""
        with self.assertRaises(ValueError) as context:
            collection.Dict([(1, 2), (1, 3)])
        self.assertIn("must be unique", str(context.exception))
