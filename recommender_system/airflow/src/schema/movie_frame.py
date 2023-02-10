from pyspark.sql.types import ArrayType, StructType, StructField, StringType, DoubleType, LongType


RECOMMENDATION = StructType(fields=[
    StructField(name='user_id', dataType=StringType(), nullable=True),
    StructField(name='movies_id', dataType=ArrayType(elementType=StringType()), nullable=True),
])

ALS = StructType(fields=[
    StructField(name='user_id', dataType=StringType(), nullable=True),
    StructField(name='movie_id', dataType=StringType(), nullable=True),
    StructField(name='metric', dataType=DoubleType(), nullable=True),
])

METADATA = StructType(fields=[
    StructField(name='id', dataType=StringType(), nullable=True),
    StructField(name='duration', dataType=LongType(), nullable=True),
])

OLAP = StructType(fields=[
    StructField(name='user_id', dataType=StringType(), nullable=True),
    StructField(name='movie_id', dataType=StringType(), nullable=True),
    StructField(name='metric', dataType=DoubleType(), nullable=True),
])
