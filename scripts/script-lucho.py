~gdalinfo ~/clase15/images/imagen_0.tif

source ~/OTB-7.2.0-Linux64/otbenv.profile

export OTB_MAX_RAM_HINT=10240
export GDAL_CACHEMAX=10240

# Optical radiometric calibration - NO

otbcli_OpticalCalibration \
-in  ~/clase15/images/imagen_0.tif \
-level toa \
-out ~/clase15/images/imagen_0_0_orc.tif
# FALTAN LAS FECHAS Y HORARIOS



# NDVI

otbcli_BandMathX \
-il ~/clase15/images/imagen_0.tif \
-exp "ndvi(im1b1,im1b4)" \
-out ~/clase15/results/imagen_0_0_ndvi.tif \
-ram 12240

# Images with no-data values - IMPUTACION

otbcli_ManageNoData \
-in ~/clase15/results/imagen_0_0_ndvi.tif \
-out ~/clase15/results/imagen_0_1_mask.tif \
-mode buildmask \
-ram 12240

otbcli_BandMath \
-il ~/clase15/images/imagen_0.tif \
-out ~/clase15/results/imagen_0_2_filtered.tif \
-exp "2*im1b1-4" \
-ram 12240

otbcli_ManageNoData \
-in ~/clase15/results/imagen_0_2_filtered.tif \
-out ~/clase15/results/imagen_0_3_imputed.tif \
-mode apply \
-mode.apply.mask ~/clase15/results/imagen_0_1_mask.tif \
-ram 12240

gdalinfo ~/clase15/results/imagen_0_3_imputed.tif

# COMPRESS
gdal_translate \
-co COMPRESS=LZW \
~/clase15/results/imagen_0_3_imputed.tif \
~/clase15/results/imagen_0_3b_compressed.tif

# Enhance local contrast

otbcli_ContrastEnhancement \
-in ~/clase15/results/imagen_0_3b_compressed.tif \
-out ~/clase15/results/imagen_0_5_contrasted.tif \
-spatial global \
-ram 12240


otbcli_DimensionalityReduction \
-in ~/clase15/results/imagen_0_5_contrasted.tif \
-out ~/clase15/results/imagen_0_6_pca.tif \
-method napca \
-method.napca.radiusx 10 \
-method.napca.radiusy 10 \
-nbcomp 3 \
-normalize true \
-ram 8092


# NOSE
otbcli_LocalRxDetection \
-in ~/clase15/results/imagen_0_6_pca.tif \
-out ~/clase15/results/imagen_0_7_rx.tif \
-ir 1 \
-er 5 \
-ram 12240





otbcli_MeanShiftSmoothing \
-in ~/clase15/results/imagen_0_6_pca.tif \
-fout ~/clase15/results/imagen_0_7_smoothed.tif \
-foutpos ~/clase15/results/imagen_0_7_smoothed_pos.tif \
-spatialr 20 \
-ranger 5 \
-maxiter 30 \
-ram 12240

# Large-Scale Mean-Shift (LSMS) segmentation

otbcli_LargeScaleMeanShift \
-in ~/clase15/results/imagen_0_7_smoothed.tif \
-tilesizex 512 \
-tilesizey 512 \
-spatialr 20 \
-ranger 50 \
-minsize 64 \
-mode.vector.out ~/clase15/results/imagen_0_5_segmented.shp \
-ram 12240


# CLASIFICACION POR PIXEL

otbcli_ComputeImagesStatistics \
-il ~/clase15/results/imagen_0_7_smoothed.tif \
-out ~/clase15/results/imagen_0_7_smoothed_stats.xml \
-ram 12240

otbcli_TrainImagesClassifier \
-io.il ~/clase15/results/imagen_0_7_smoothed.tif \
-io.vd ~/clase15/data/segments_entrenamiento.geojson \
-io.imstat ~/clase15/results/imagen_0_7_smoothed_stats.xml \
-sample.vtr 0.80 \
-sample.vfn uso \
-classifier dt \
-classifier.dt.max 10 \
-io.out ~/clase15/results/DTModel.txt \
-io.confmatout ~/clase15/results/ConfusionMatrixDT.csv \
-ram 12240


otbcli_ImageClassifier \
-in ~/clase15/results/imagen_0_7_smoothed.tif \
-imstat ~/clase15/results/imagen_0_7_smoothed_stats.xml \
-model ~/results/dTModel.txt \
-out ~/results/aoi0_labeled.tif \
-ram 12240

####

otbcli_ComputeOGRLayersFeaturesStatistics\
-inshp ~/clase15/results/vector_class_train.shp \
-outstats ~/clase15/clase15/results/vector_class_train_stats.xml \
-feat nbPixels meanB0 meanB1 meanB2 meanB3 varB0 varB1 varB2 varB3 

otbcli_TrainVectorClassifier \
-io.vd ~/clase15/clase15/results/vector_class_train.shp \
-io.stats ~/clase15/clase15/results/vector_class_train_stats.xml \
-cfield class \
-classifier dt \
-classifier.dt.max 10 \
-io.out ~/clase15/clase15/results/dTModel_obia.txt \
-io.confmatout ~/clase15/clase15/results/ConfusionMatrixDT_obia.csv \
-feat nbPixels meanB0 meanB1 meanB2 meanB3 varB0 varB1 varB2 varB3
