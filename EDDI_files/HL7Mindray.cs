
using Eddi.Core.DataModels;
using Eddi.Core.Util;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Media;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Threading.Tasks;

namespace HL7Soup.Interpreter.Providers
{
	public static class HL7Mindray
	{
		//Read all data observations in the  message
		public static PhysiologicalData ReadPhysiologicalData(List<HL7Observation> observations,DateTime messagetime)
		{
			//Initalise Data to Map values
			DataMap mappedData = new DataMap();

			//mappedData.Time = messagetime;
			mappedData.Time = messagetime;

			//Convert each observation type
			foreach (HL7Observation o in observations)
			{
				//Confirm observation of interest
				if (mindray_hl7_datacoding.Any(x=>x.Value.OBX_3_2 == o.Identifier.OBX3_2))
				{
					//store the observation data
					var dictElement = mindray_hl7_datacoding.First(x => x.Value.OBX_3_2 == o.Identifier.OBX3_2);

					var name = dictElement.Key;
					var value = o.Value;

					// Create an instance of the target class
					EDDIDataMapping.MapProperties(name,o.Value, ref mappedData);
				}
			}

			//Add Values for speical elements
			BloodPressure invasive = new BloodPressure(mappedData.BP1_SYS,mappedData.BP1_DIA,mappedData.BP1_MEAN);
			BloodPressure nonInvasive = new BloodPressure();
			HeartRate heartRate = new HeartRate(mappedData.PR_ECG,mappedData.PR_BP1,mappedData.PR_spO2);

			//Create the data
			PhysiologicalData data = new PhysiologicalData(mappedData.Time,
				invasive,
				nonInvasive,
				heartRate,
				mappedData.Pv,
				mappedData.CO2_Et,
				mappedData.CO2_Fi,
				mappedData.CO2_RR,
				mappedData.SPO2_Sat,
				mappedData.Mac_Sum,
				mappedData.Temp,
				mappedData.Ppv);

			return data;
		}



		private static Dictionary<string, HL7ParameterType> mindray_hl7_datacoding = new Dictionary<string, HL7ParameterType>()
		{
			{"IBP1SYS", new HL7ParameterType("NM",150017,"MDC_PRESS_BLD_SYS","MDC","MDC_DIM_MMHG",1)},
			{"IBP1DIA", new HL7ParameterType("NM",150018,"MDC_PRESS_BLD_DIA","MDC","MDC_DIM_MMHG",1)},
			{"IBP1MEAN", new HL7ParameterType("NM",150019,"MDC_PRESS_BLD_MEAN","MDC","MDC_DIM_MMHG",1)},
			{"IBP1PR", new HL7ParameterType("NM",150019,"MDC_BLD_PULS_RATE_INV","MDC","MDC_DIM_BEAT_PER_MIN",1)},
			{"NIBP1SYS", new HL7ParameterType("NM",150021,"MDC_PRESS_BLD_NONINV_SYS","MDC","MDC_DIM_MMHG",1)},
			{"NIBP1DIA", new HL7ParameterType("NM",150022,"MDC_PRESS_BLD_NONINV_DIA","MDC","MDC_DIM_MMHG",1)},
			{"NIBP1MEAN", new HL7ParameterType("NM",150023,"MDC_PRESS_BLD_NONINV_MEAN","MDC","MDC_DIM_MMHG",1)},
			{"SPO2_PR",new HL7ParameterType("NM",149530,"MDC_PULS_OXIM_PULS_RATE","MDC","MDC_DIM_PERCENT",1)},
			{"SPO2_SAT",new HL7ParameterType("NM",150456,"MDC_PULS_OXIM_SAT_O2","MDC","MDC_DIM_PERCENT",1)},
			{"SPO2_PV",new HL7ParameterType("NM",478,"MNDRY_PULS_OXIM_PLETH_VAR_INDEX","99MNDRY","MDC_DIM_PERCENT",1)},
			{"QT_HR_CURRENT",new HL7ParameterType("NM",307,"MNDRY_ECG_QTC_HR","99MNDRY","MDC_DIM_BEAR_PER_MIN",1)},
			{"Et_CO2",new HL7ParameterType("NM",151708,"MDC_CONC_AWAY_CO2_ET","MDC","MDC_DIM_MMHG",1)},
			{"Fi_CO2" , new HL7ParameterType("NM", 151716, "MDC_CONC_AWAY_CO2_INSP", "MDC", "MDC_DIM_MMHG", 1) },
			{"RR_CO2" , new HL7ParameterType("NM", 151594, "MDC_CO2_RESP_RATE", "MDC", "MDC_DIM_RESP_PER_MIN", 1) },
			{"MAC" , new HL7ParameterType("NM", 152872, "MDC_CONC_MAC", "MDC", "MDC_DIM_DIMLESS", 1) },
			{"TEMP1_ART", new HL7ParameterType("NM",150352,"MDC_TEMP_ART","MDC","MDC_DIM_FAHR",1)},
			{"PPV",new HL7ParameterType("NM",153,"MNDRY_PRESS_PULSE_VARIATION","99MNDRY","MDC_DIM_PERCENT",1)}
		};

	}
}
