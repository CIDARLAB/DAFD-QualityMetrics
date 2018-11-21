"""A graphical interface to our interpolation modeller"""
from core_logic.ForwardModel import ForwardModel
from core_logic.InterModel import InterModel
from helper_scripts.ModelHelper import ModelHelper
import tkinter
from PIL import ImageTk, Image
from tkinter import ttk
import tkinter.messagebox

class DAFD_GUI:
	"""A class that produces a windowed interface for DAFD"""

	def __init__(self):
		"""Initialize the GUI components"""
		self.root = tkinter.Tk()
		self.root.title("DAFD")


		#Attach the interpolation model to the GUI
		self.it = InterModel()

		self.MH = ModelHelper.get_instance() # type: ModelHelper

		self.ranges_dict = self.MH.ranges_dict
		self.input_headers = self.MH.input_headers
		self.output_headers = self.MH.output_headers

		# DAFD Logo
		img = Image.open(self.MH.resource_path("DAFD_logo.png"))
		img = ImageTk.PhotoImage(img.resize((int(0.1*img.size[0]), int(0.1*img.size[1])), Image.ANTIALIAS))
		panel = tkinter.Label(self.root, image=img)
		panel.pack(side="top", fill="both")
		panel.configure(background="white")
		self.root.configure(background="white")

		#Pack all input constraint elements together
		inputs_frame = tkinter.Frame(self.root)
		inputs_frame.pack(side="top")
		inputs_frame.configure(background="white")

		inputs_header = tkinter.Label(inputs_frame)
		inputs_header.pack(side="top")
		inputs_header["text"] = "Constraints"
		inputs_header.config(font=("Times", 20))
		inputs_header.configure(background="white")

		self.entries_dict = {}

		for param_name in self.input_headers:
			param_frame = tkinter.Frame(inputs_frame)
			param_frame.pack(side="top")
			param_frame.configure(background="white")
			param_label = tkinter.Label(param_frame,width=40,anchor="e")
			param_label.pack(side="left")
			param_label["text"] = param_name + " (" + str(round(self.ranges_dict[param_name][0],2)) + "-" + str(round(self.ranges_dict[param_name][1],2)) + ") : "
			param_label.configure(background="white")
			param_entry = tkinter.Entry(param_frame)
			param_entry.pack(side="left")
			param_entry.configure(background="white")
			self.entries_dict[param_name] = param_entry

		#Pack the desired output elements together
		outputs_frame = tkinter.Frame(self.root,pady=20)
		outputs_frame.pack(side="top")
		outputs_frame.configure(background="white")

		outputs_header = tkinter.Label(outputs_frame)
		outputs_header.pack(side="top")
		outputs_header["text"] = "Desired Values"
		outputs_header.config(font=("Times", 20))
		outputs_header.configure(background="white")

		for param_name in self.output_headers:
			param_frame = tkinter.Frame(outputs_frame)
			param_frame.pack(side="top")
			param_frame.configure(background="white")
			param_label = tkinter.Label(param_frame,width=40,anchor="e")
			param_label.pack(side="left")
			param_label["text"] = param_name + " (" + str(round(self.ranges_dict[param_name][0],2)) + "-" + str(round(self.ranges_dict[param_name][1],2)) + ") : "
			param_label.configure(background="white")
			param_entry = tkinter.Entry(param_frame)
			param_entry.pack(side="left")
			param_entry.configure(background="white")
			self.entries_dict[param_name] = param_entry



		#Pack the results together
		results_frame = tkinter.Frame(self.root,pady=20)
		results_frame.pack(side="top")
		results_frame.configure(background="white")
		submit_dafd_button = ttk.Button(results_frame, text='Run DAFD',command = self.runInterp)
		submit_dafd_button.pack(side="top")
		submit_fwd_button = ttk.Button(results_frame, text='Run Forward Model',command = self.runForward)
		submit_fwd_button.pack(side="top")
		self.results_label = tkinter.Label(results_frame)
		self.results_label.pack(side="top")
		self.results_label.configure(background="white")

		
		#Start everything
		self.root.mainloop()


	def runInterp(self):
		"""Predict an input set based on given constraints and desired outputs"""

		#Get all of our constraints
		constraints = {}
		for param_name in self.input_headers:
			param_entry = self.entries_dict[param_name].get()
			if param_entry != "":
				#The constraint can either be a single value or a range
				if "-" in param_entry:
					#If it is a range x to y, the range is x-y
					pair = param_entry.split("-")
					wanted_constraint = (float(pair[0]),float(pair[1]))
				else:
					#If it is a single value x, the range is x-x
					wanted_constraint = (float(param_entry),float(param_entry))

				if wanted_constraint[0] <= self.ranges_dict[param_name][0]:
					tkinter.messagebox.showwarning("Out of range constraint",param_name + " was too low. Constraint ignored")
				elif wanted_constraint[1] >= self.ranges_dict[param_name][1]:
					tkinter.messagebox.showwarning("Out of range constraint",param_name + " was too high. Constraint ignored")
				else:
					constraints[param_name] = wanted_constraint

		# Get the desired outputs
		# Note one can be left blank, in which case the interpolation model will simply operate on the other value's model
		desired_vals = {}
		for param_name in self.output_headers:
			param_entry = self.entries_dict[param_name].get()
			if param_entry != "":
				wanted_val = float(param_entry)
				if wanted_val >= self.ranges_dict[param_name][0] and wanted_val <= self.ranges_dict[param_name][1]:
					desired_vals[param_name] = wanted_val
				else:
					tkinter.messagebox.showwarning("Out of range desired value", param_name + " was out of range. Value was ignored")

		#Return and display the results
		results = self.it.interpolate(desired_vals,constraints)
		self.results_label["text"] = "\n".join([x + " : " + str(results[x]) for x in self.input_headers])
	
	def runForward(self):
		"""Predict the outputs based on the chip geometry (Normal feed-forward network) """

		#Get all the chip geometry values
		features = {}
		features = {x: float(self.entries_dict[x].get()) for x in self.input_headers}
		raw_features = [features[x] for x in self.input_headers]
		fwd_model = ForwardModel()
		outs = fwd_model.predict(raw_features)
		self.results_label["text"] = "\n".join([x + " : " + str(outs[x]) for x in outs])



#Executed when script is called from console
DAFD_GUI()
