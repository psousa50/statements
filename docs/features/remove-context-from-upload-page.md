# Remove Context from Upload Page

The context provider is not a good idea here. Let's remove it and use only state hook.

There should be a useState for:
 - file
 - sourceId
 - isAnalyzing
 - analysisResult
 - isUploading
 - uploadResult
 - columnMappings
 - uploadFileSpec

 this should be enough, add more if needed.

 The AnalysisSummary should receive only:
 - sources
 - analysisResult
 - columnMappings
 - 
 
 
 